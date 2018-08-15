
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

UpdateData.prototype.onopen = function () {
    var prjName = jQuery("#project-name").val().trim();
    var svnHost = jQuery("#svn-host").val().trim();
    var user    = jQuery("#git-username").val().trim();
    var password = jQuery("#git-password").val().trim();
    var localSaveRoad = jQuery("#svn-save").val().trim();

    var data = {
        type: "svnUpdate",
        name: prjName,
        host: svnHost,
        username: user,
        password: password,
        localRoad: localSaveRoad
    };

    var jsonQueryInfo =  JSON.stringify(data);
    window.socket.send(jsonQueryInfo);
    jQuery("#myModal").modal('hide');
    jQuery("#modal_info").show();
    // window.location.reload(true);
};
UpdateData.prototype.onmessage = function(msg){
    if (typeof msg.data == "string") {
        if  (isNaN(Number(msg.data)))
        {
            // 显示查询结果代码
            var json_obj = JSON.parse(msg.data);
            if ("type" in json_obj)
            {
                var type = json_obj["type"];
                if (type === "not_found")
                {
                    console.log("not_found");
                    jQuery("#not-found").show();
                }
                if(type === "update_files")
                {
                    console.log(json_obj["finish_precent"]);
                    var update_progress_group = jQuery("#update-progress-group");
                    update_progress_group.show();
                    var update_progressbar = jQuery("#update-progressbar");
                    update_progressbar.width(json_obj["finish_precent"]);
                    update_progressbar.text("已更新:" + json_obj["finish_precent"]);


                    var show_error_info = jQuery("#show_error_info");
                    var show_error_file = jQuery("#show_error_files");
                    if (json_obj["filename"])
                    {
                        show_error_info.show();
                        show_error_file.append("<li>"+ json_obj["filename"] + "</li>");
                    }
                }
            }
            // 有数据
            var datas = json_obj["datas"];
            var html = template('query-item',{"datas": datas});
            var show_excel = jQuery("#show_excel");
            show_excel.append(html);
        }else{
            // 进度条的代码
            progress.text(msg.data +  '% Complete (success)');
            progress.css({"width": msg.data + '%'});
        }
    }
    else {
        alert("非文本消息");
    }
};

UpdateData.prototype.listenShowHideEvent = function() {
    var self = this;
    var submitLocal =  jQuery('#submit-local');
    submitLocal.click(function (e) {
        e.preventDefault();
        var show_error_file = jQuery("#show_error_files");
        show_error_file.children('li').remove();
        jQuery("#progress-group").hide();
        jQuery("#not-found").hide();
        var prjName = jQuery("#project-name").val().trim();
        jQuery(".project-name").text(prjName);
        if (window.socket == null)
        {
            var host = "ws://10.240.113.164:9005/";
            window.socket = new WebSocket(host);
            window.socket.onopen = function (msg) {
                self.onopen();
            }
        }else{
            self.onopen();
        }
        window.socket.onmessage = function (msg) {
                self.onmessage(msg);
            }
    });
};

UpdateData.prototype.run = function () {
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
    var self = this;
    jQuery("#update-progress-group").hide();
    jQuery("#show_error_info").hide();
    jQuery("#modal_info").hide();
    if(window.socket == null){
        var host = "ws://10.240.113.164:9005/";
        self.socket = new WebSocket(host);
        window.socket = self.socket;
        jQuery("#progress-group").show();
        var progress = jQuery("#progressbar")
        progress.css({"width": 0});
        progress.text('0.0% Complete (success)');
        var show_excel = jQuery("#show_excel");
        show_excel.html("");
        try {
            self.socket.onopen = function (msg) {
                var queryInfo = new Object();
                queryInfo.type = "queryInfo";
                queryInfo.keyword = jQuery("#inputKeyword").val();
                if(queryInfo.keyword.length !== 0)
                {
                    console.log("not empyt");
                    queryInfo.queryMode = jQuery("#select-type").val();
                    queryInfo.tableType = jQuery("#table-type1").val();
                    queryInfo.selectScope = jQuery("#select-scope").val();

                    var jsonQueryInfo =  JSON.stringify(queryInfo);
                    self.socket.send(jsonQueryInfo);
                }else{
                    console.log("empty");
                }
            };

            self.socket.onmessage = function (msg) {
                if (typeof msg.data == "string") {
                    // displayContent(msg.data);
                    if  (isNaN(Number(msg.data)))
                    {
                        // 显示查询结果代码
                        var json_obj = JSON.parse(msg.data);
                        if ("type" in json_obj)
                        {
                            var type = json_obj["type"];
                            if (type === "not_found")
                            {
                                console.log("not_found");
                                jQuery("#not-found").show();
                            }
                            if (type === "badFiles")
                            {
                                console.log("badFiles Test");
                            }
                        }
                        // 有数据
                        var datas = json_obj["datas"];
                        var html = template('query-item',{"datas": datas});
                        var show_excel = jQuery("#show_excel");
                        show_excel.append(html);
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
    }else{
        jQuery("#not-found").hide();
        self.socket = window.socket;
        jQuery("#progress-group").show();
        var progress = jQuery("#progressbar")
        progress.css({"width": 0});
        progress.text('0.0% Complete (success)');
        var show_excel = jQuery("#show_excel");
        show_excel.html("");
        try {
            // self.socket.onopen = function (msg) {
                var queryInfo = new Object();
                queryInfo.type = "queryInfo";
                queryInfo.keyword = jQuery("#inputKeyword").val();
                if(queryInfo.keyword.length !== 0)
                {
                    console.log("not empyt");
                    queryInfo.queryMode = jQuery("#select-type").val();
                    queryInfo.tableType = jQuery("#table-type1").val();
                    queryInfo.selectScope = jQuery("#select-scope").val();

                    var jsonQueryInfo =  JSON.stringify(queryInfo);
                    self.socket.send(jsonQueryInfo);
                }else{
                    console.log("empty");
                }
            // };

            self.socket.onmessage = function (msg) {
                if (typeof msg.data == "string") {
                    // displayContent(msg.data);
                    if  (isNaN(Number(msg.data)))
                    {
                        // 显示查询结果代码
                        var json_obj = JSON.parse(msg.data);
                        if ("type" in json_obj)
                        {
                            var type = json_obj["type"];
                            if (type === "not_found")
                            {
                                console.log("not_found");
                                jQuery("#not-found").show();
                            }
                            if (type === "badFiles")
                            {
                                console.log("badFiles Test");
                            }
                        }
                        // 有数据
                        var datas = json_obj["datas"];
                        var html = template('query-item',{"datas": datas});
                        var show_excel = jQuery("#show_excel");
                        show_excel.append(html);
                    }else{
                        // {#进度条的代码#}
                        // var progress = jQuery("#progressbar")
                        progress.text(msg.data +  '% Complete (success)');
                        progress.css({"width": msg.data + '%'});
                        console.log(progress.width);
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
    });
    jQuery("#reset-search").click(function () {
        jQuery(".form-horizontal")[0].reset();
    });

    window.socket = null;

    // jQuery("#svn-save").click(function () {
    //     console.log("这是一个点击事件");
    //      var fileSave = new ActiveXObject("MSComDlg.CommonDialog");
    //     fileSave.MaxFileSize = 128;
    //     fileSave.Filter = "*.bmp";
    //     fileSave.FilterIndex = 2;
    //     fileSave.fileName = mydate.toLocaleString().replace(" ", "").replace("年", "").replace("月", "").replace("日", "").replace(reg, "");
    //     fileSave.DialogTitle = "选择图片存储路径";
    //     fileSave.ShowSave();
    //     var path=fileSave.fileName+".bmp";
    // });
});