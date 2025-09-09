import pandas as pd
import re
from io import BytesIO  # 用于处理上传的文件流


def process_data(file_content, sheet_name="Sheet1"):
    """
    处理上传的Excel文件内容，返回处理后的Excel文件流

    参数:
        file_content: 上传的Excel文件二进制内容（从前端获取）
        sheet_name: 要读取的工作表名称，默认"Sheet1"

    返回:
        BytesIO: 处理后的Excel文件流，可直接用于前端下载
    """
    try:
        # 第一步：数据提取
        df = pd.read_excel(BytesIO(file_content), sheet_name=sheet_name, header=[2, 3])

        # 定义筛选列（多级索引）
        signal_type_col = ('信号\n类型', 'Unnamed: 7_level_1')
        address_col = ('信息对象地址（十进制）', 'Unnamed: 13_level_1')

        # 筛选DIB信号或地址在16358-20479之间的数据
        df_filtered = df[
            (df[signal_type_col] == 'DIB') |
            ((df[address_col] > 16358) & (df[address_col] < 20480))
            ].sort_index()

        # 提取目标列
        target_columns = [
            ("信号ID", ""),
            ("信号\n类型", ""),
            ("信号所属设备ID", ""),
            ("DI/DO 信号取值定义", "取值0"),
            ("DI/DO 信号取值定义", "取值1"),
            ("AI对象相关参数", "单位")
        ]

        result_df = pd.DataFrame()
        for col in target_columns:
            col_tuple = (col[0], col[1]) if col[1] else (col[0],)
            if col_tuple in df_filtered.columns:
                col_name = f"{col[0]}-{col[1]}" if col[1] else col[0]
                result_df[col_name] = df_filtered[col_tuple]

        # 第二步：数据清洗（仅保留设备ID中的中文字符）
        def extract_chinese(text):
            return ''.join(re.findall(r'[\u4e00-\u9fff]', str(text)))

        result_df['信号所属设备ID_清洗'] = result_df['信号所属设备ID'].apply(extract_chinese)

        # 第三步：数据筛选（去重）
        grouped = result_df.groupby(['信号所属设备ID', '信号所属设备ID_清洗'])['信号ID'] \
            .apply(lambda x: tuple(sorted(set(x)))) \
            .reset_index()

        unique_groups = grouped.drop_duplicates(
            subset=['信号所属设备ID_清洗', '信号ID'],
            keep='first'
        ).reset_index(drop=True)

        # 提取去重后的设备ID对应的记录
        valid_device_ids = unique_groups['信号所属设备ID'].tolist()
        filtered_df = result_df[result_df['信号所属设备ID'].isin(valid_device_ids)]
        filtered_df = filtered_df.drop(columns=['信号所属设备ID_清洗'])

        # 第四步：准备最终数据（重命名、排序、加列）
        column_mapping = {
            '信号ID': 'AttrsName',
            '信号\n类型': 'DataType',
            '信号所属设备ID': 'DeviceID',
            'DI/DO 信号取值定义-取值0': 'OffMsg',
            'DI/DO 信号取值定义-取值1': 'OnMsg',
            'AI对象相关参数-单位': 'EngUnits'
        }

        renamed_df = filtered_df.rename(columns=column_mapping)

        # 按 DataType（DIB在前）和 DeviceID 排序
        type_order = {'DIB': 0, 'AIS': 1}
        renamed_df['_sort_key'] = renamed_df['DataType'].map(type_order).fillna(2)
        sorted_df = renamed_df.sort_values(by=['_sort_key', 'DeviceID']).drop(columns=['_sort_key'])

        # 添加 ID 和 TempletName 列
        sorted_df['ID'] = range(1, len(sorted_df) + 1)
        sorted_df['TempletName'] = sorted_df['DeviceID']

        # 调整列顺序
        final_columns = [
            'ID', 'TempletName', 'AttrsName', 'DeviceID',
            'DataType', 'OffMsg', 'OnMsg', 'EngUnits'
        ]
        final_df = sorted_df.reindex(columns=final_columns, fill_value='')  # 缺失列用空值填充

        local_save_path = "E:/python_code/7000tool/处理结果.xlsx"  # 自定义路径，如 "./output/处理结果.xlsx"
        final_df.to_excel(local_save_path, index=False, engine='openpyxl')
        # 将结果写入BytesIO流（用于前端下载）
        output = BytesIO()
        final_df.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)  # 重置文件指针到开头

        return output

    except Exception as e:
        # 抛出异常，由app.py捕获并返回错误信息
        raise Exception(f"数据处理失败：{str(e)}")