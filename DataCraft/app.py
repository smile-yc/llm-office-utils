from flask import Flask, render_template, request, send_file
import processing.modelcfg_pro

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')  # 直接返回前端页面

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "未上传文件", 400
    file = request.files['file']
    try:
        # 调用数据处理逻辑（根据实际模块路径调整导入）
        processed_file = processing.modelcfg_pro.process_data(file.read())
        return send_file(
            processed_file,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            download_name='处理结果.xlsx'
        )
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    app.run(debug=True)