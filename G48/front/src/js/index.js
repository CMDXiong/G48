
function ProgressBar() {
}

ProgressBar.prototype.listenProgressBarEvent = function() {
    var self = this
    // var btn_search = $("#btn-search")
    $("#btn-search").click(function (event) {
        console.log('iscoming');
        var ws = new WebSocket("ws://127.0.0.1:8001");
        ws.onopen = function (msg) {
            alert("连接成功！");
        };
        ws.onmessage = function (msg) {
            $("#progressbar").val(10)
            if (typeof msg.data == "int") {
                // displayContent(msg.data);
                $("#progressbar").val(msg.data)
            }
            else {
                alert("不是整型");
            }
        };
    });
};

ProgressBar.prototype.run = function () {
    console.log('构造函数');
    // this.listenProgressBarEvent();
};

$(function () {
    var progressbar = new ProgressBar();
    progressbar.run();
});

function UpdateData() {
    var self = this;
    self.maskWrapper = jQuery('.mask-wrapper');
}

UpdateData.prototype.showEvent = function() {
    var self = this;
    self.maskWrapper.show();
};

UpdateData.prototype.hideEvent = function() {
    var self = this;
};

UpdateData.prototype.listenShowHideEvent = function() {
    var self = this;
    var submitLocal =  jQuery('#submit-local');
    submitLocal.click(function (e) {
        e.preventDefault();
        var prjName = jQuery("#project-name").val().trim();
        var svnHost = jQuery("#svn-host").val().trim();
        var user    = jQuery("#git-username").val().trim();
        var password = jQuery("#git-password").val().trim();
        var localsaveroad = "C:\\Users\\panxiong\\Desktop\\pan_test_4";
        console.log("******************")
        console.log(prjName);
        console.log(svnHost);
        console.log(user);
        console.log(password);
        console.log(localsaveroad);

        // window.location.reload(true);
    });
};

UpdateData.prototype.run = function () {
    console.log("1");
    var self = this;
    self.listenShowHideEvent();
};

$(function () {
    var update = new UpdateData();
    update.run();
});

function QueryBtn() {
    var self = this;
    self.queryBtn = jQuery("#btn-search");
}

QueryBtn.prototype.listenClickEnterEvent = function (){
    var self = this;
    self.queryBtn.click(function () {
        self.connectionEvent();
    });
    self.queryBtn.keypress(function (e) {
        if (e.keyCode == 13)
            self.connectionEvent();
    });
};


QueryBtn.prototype.connectionEvent = function () {
    console.log("connect");
    var self = this;
    var host = "ws://10.240.113.164:9005/";
    self.socket = new WebSocket(host);
    jQuery("#progress-group").show();
    var progress = jQuery("#progressbar")
    progress.css({"width": 0});
    progress.text('0.0% Complete (success)');
    var show_excel = jQuery("#show_excel");
    show_excel.html("");
    try {
        self.socket.onopen = function (msg) {
            var queryInfo = new Object();
            queryInfo.keyword = jQuery("#inputKeyword").val();
            if(queryInfo.keyword.length !== 0)
            {
                console.log("not empyt");
                queryInfo.queryMode = jQuery("#select-type").val();
                queryInfo.tableType = jQuery("#table-type1").val();
                queryInfo.selectScope = jQuery("#select-scope").val();

                var jsonQueryInfo =  JSON.stringify(queryInfo)
                self.socket.send(jsonQueryInfo);
            }else{
                console.log("empty");
            }
            // socket.send(keyword);
            // socket.send("你的连接成功");
        };

        self.socket.onmessage = function (msg) {
            if (typeof msg.data == "string") {
                // displayContent(msg.data);
                if  (isNaN(Number(msg.data)))
                {
                    // 显示查询结果代码
                    var json_obj = JSON.parse(msg.data);
                    // 有数据
                    var datas = json_obj["datas"]
                    var html = template('query-item',{"datas": datas});
                    var show_excel = jQuery("#show_excel");
                    show_excel.append(html)
                }else{
                    // {#进度条的代码#}
                    // var progress = jQuery("#progressbar")
                    progress.text(msg.data +  '% Complete (success)');
                    progress.css({"width": msg.data + '%'});
                }
            }
            else {
                alert("非文本消息");
            }
        };

        self.socket.onclose = function (msg) { alert("socket closed!") };
    }
    catch (ex) {
        log(ex);
    }
};

QueryBtn.prototype.run = function() {
    var self = this;
    self.listenClickEnterEvent();
};

$(function () {
    var queryBtnOj = new QueryBtn();
    queryBtnOj.run();
    var inputKeyword = jQuery("#inputKeyword");
    inputKeyword.keypress(function (e) {
        if (e.keyCode == 13)
            queryBtnOj.connectionEvent();
    })
});