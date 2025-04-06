$(function () {
    function bindCaptchaBtnClick() {
        $("#captcha-btn").click(function (event) {
            let $this = $(this);
            let email = $("input[name='email']").val();
            if (!email) {
                alert("请输入邮箱");
                return;
            }
            //取消按钮的点击事件
            $this.off('click');

            //发送ajax请求
            $.ajax(
                "/myauth/captcha?email="+email,{
                    method: "GET",
                    success: function (result) {
                        if (result['code'] == 200){
                            alert("验证码发送成功")
                        }else {
                            alert(result['message'])
                        }
                    },
                    fail: function (error) {
                        console.log(error);
                    }

            })

            let countdown = 60; //倒计时
            let timer = setInterval(function () {
                if (countdown <= 0) {
                    $this.text("获取验证码");
                    clearInterval(timer);
                    //重新绑定点击事件
                    bindCaptchaBtnClick();
                } else {
                    $this.text(countdown + "s");
                    countdown--;
                }
            }, 1000)

        })
    }

    bindCaptchaBtnClick();
});