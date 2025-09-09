// 页面加载完成后绑定事件
document.addEventListener("DOMContentLoaded", function () {
  const uploadBtn = document.getElementById("upload-btn");
  const excelFile = document.getElementById("excel-file");
  const progressStatus = document.getElementById("progress-status");
  const downloadLink = document.getElementById("download-link");
  const resultSection = document.querySelector(".result-section");
  const errorSection = document.querySelector(".error-section");
  const errorMsg = document.getElementById("error-msg");

  // 上传按钮点击事件
  uploadBtn.addEventListener("click", function () {
    const file = excelFile.files[0];
    if (!file) {
      showError("请先选择要上传的 Excel 文件！");
      return;
    }

    // 显示进度状态
    progressStatus.textContent = "正在上传并处理文件...";
    resultSection.style.display = "block";
    errorSection.style.display = "none";
    downloadLink.style.display = "none";

    // 构建 FormData
    const formData = new FormData();
    formData.append("file", file);

    // 调用 Flask 接口
    fetch("/upload", {
      method: "POST",
      body: formData
    })
    .then(response => {
      if (!response.ok) {
        return response.text().then(text => { throw new Error(text); });
      }
      return response.blob();
    })
    .then(blob => {
      // 处理成功，生成下载链接
      progressStatus.textContent = "处理完成！";
      const url = URL.createObjectURL(blob);
      downloadLink.href = url;
      downloadLink.download = "处理结果.xlsx";
      downloadLink.style.display = "inline-block";
    })
    .catch(error => {
      // 处理失败，显示错误信息
      showError(error.message);
    });
  });

  // 错误提示函数
  function showError(msg) {
    progressStatus.textContent = "处理失败！";
    errorMsg.textContent = msg;
    errorSection.style.display = "block";
    downloadLink.style.display = "none";
  }
});