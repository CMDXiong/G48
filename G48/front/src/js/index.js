
function UpdateData() {
    var self = this;
    self.maskWrapper = jQuery('.mask-wrapper');
}

UpdateData.prototype.listenShowHideEvent = function() {
    var self = this;
    var submitLocal =  jQuery('#submit-local');
    submitLocal.click(function (e) {
        e.preventDefault();
        window.svn_config = true;
        jQuery("#progress-group").hide();
        jQuery("#not-found").hide();
        var prjName = jQuery("#project-name").val().trim();
        jQuery(".project-name").text(prjName);

        // var host = "ws://10.240.113.164:9005/";
        var address = window.location.hostname;
        var host = "ws://" + address + ":9005/";
        var socket = new WebSocket(host);
        try {
            socket.onopen = function (msg) {
                var prjName       = jQuery("#project-name").val().trim();
                var svnHost       = jQuery("#svn-host").val().trim();
                var user          = jQuery("#git-username").val().trim();
                var password      = jQuery("#git-password").val().trim();
                var localSaveRoad = jQuery("#svn-save").val().trim();

                if ((prjName === "") || (svnHost === "") || (user === "") || (password === "") || (localSaveRoad == "")) {
                    alert('必填项不能为空！');
                    return;
                }
                var data = {
                    type: "svnUpdate",
                    name: prjName,
                    host: svnHost,
                    username: user,
                    password: password,
                    localRoad: localSaveRoad
                };

                var jsonQueryInfo =  JSON.stringify(data);
                socket.send(jsonQueryInfo);
                jQuery("#myModal").modal('hide');
                jQuery("#modal_info").show();
                // window.location.reload(true);
            }
            socket.onmessage = function (msg) {
                if (typeof msg.data == "string") {
                    var json_obj = JSON.parse(msg.data);
                    var type = json_obj["type"];
                    if(type === "path_error")               // 填写的路径不正确的提示
                    {
                        alert('保存路径不存在！');
                        socket.close();
                        return ;
                    }
                    if(type === "svn_config_success")
                    {
                        alert('svn配置成功');
                        socket.close();
                        return ;
                    }
                }
            }
        }
        catch (e) {
            log(e);
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
        if (window.svn_config == false )
        {
            alert("请先配置！！！");
            return;
        }
        if (window.able_search == false )
        {
            alert("请先热更新！！！");
            return;
        }

        self.connectionEvent();
    });
    self.queryBtn.keypress(function (e) {
        if (window.svn_config == false )
        {
            alert("请先配置！！！");
            return;
        }
        if (window.able_search == false )
        {
            alert("请先热更新！！！");
            return;
        }
        if (e.keyCode == 13)
            self.connectionEvent();
    });
};

QueryBtn.prototype.connectionEvent = function () {
    var self = this;
    jQuery("#update-progress-group").hide();
    jQuery("#show_error_info").hide();
    jQuery("#modal_info").hide();

    // var host = "ws://10.240.113.164:9005/";
    var address = window.location.hostname;
    var host = "ws://" + address + ":9005/";
    var socket = new WebSocket(host);
    jQuery("#progress-group").show();
    var progress = jQuery("#progressbar")
    progress.css({"width": 0});
    progress.text('0.0% Complete (success)');
    var show_excel = jQuery("#show_excel");
    jQuery("#not-found").hide();
    show_excel.html("");
    try {
        socket.onopen = function (msg){
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
                socket.send(jsonQueryInfo);
            }else{
                console.log("empty");
            }
        }
        socket.onmessage = function (msg) {
            if (typeof msg.data == "string") {
                // 显示查询结果代码
                var json_obj = JSON.parse(msg.data);   // 反序列化
                var type = json_obj["type"];           // 传递过来的数据中一定会有type关键字，根据type来做相应的操作

                if (type === "not_found")          // 未找到相关检索的提示
                {
                    console.log("未找到相关检索，通信正常关闭");
                    socket.close();
                    jQuery("#not-found").show();
                }
                if (type ===  "more_data")
                {
                    console.log("more_data");
                    alert("关键字检索范围过大，请进一步细化关键字");
                    socket.close();
                }
                if (type === "query_finish")       // 通信完成
                {
                    console.log("正常通信关闭");
                    socket.close();
                }
                if (type === "progressbar")        // 进度条的动态显示
                {
                    console.log("progressbar");
                    progress.text(json_obj["value"] + '% Complete (success)');
                    progress.width(json_obj["value"] + '%');
                }

                if (type == "query_result")       // 显示查询的结果
                {
                    console.log("查询结果");
                    var datas = json_obj["datas"];
                    var html = template('query-item',{"datas": datas});
                    var show_excel = jQuery("#show_excel");
                    show_excel.append(html);
                }
            }
        }
        // socket.onclose = function (msg) { alert("socket closed!") }
    }
    catch (e) {
        log(e);
    }
};

QueryBtn.prototype.run = function() {
    var self = this;
    self.listenClickEnterEvent();
};

$(function () {
    window.svn_config = false;
    window.able_search = false;
    // window.svn_config = true;
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

    jQuery("#update").click(function () {                     // 点击热更新
        if (window.svn_config == false )
        {
            alert("请先配置！！！");
        }
        else
        {
            var show_error_info = jQuery("#show_error_info");
            show_error_info.find("li").remove();
            var show_excel = jQuery("#show_excel");
            jQuery("#not-found").hide();
            jQuery("#progress-group").hide();
            jQuery("#circle-progress-info").show();
            show_excel.html("");

            // var host = "ws://10.240.113.164:9005/";
            var address = window.location.hostname;
            var host = "ws://" + address + ":9005/";
            var socket = new WebSocket(host);
            var update_info = new Object();
            update_info.type = "update_request";
            var json_update_info =  JSON.stringify(update_info);
            try {
                socket.onopen = function () {
                    socket.send(json_update_info);
                }
                socket.onmessage = function (msg) {
                    if (typeof msg.data == "string") {
                        var json_obj = JSON.parse(msg.data);
                        var type = json_obj["type"];
                        if(type === "path_error")               // 填写的路径不正确的提示
                        {
                            alert('保存路径不存在！');
                            socket.close();
                        }
                        if (type === "badFiles")                 //载入数据碰到坏文件的提示
                        {
                            socket.close();
                            console.log("show badFiles")
                        }
                        if(type === "update_files")              // 更新进度条的显示
                        {
                            jQuery("#circle-progress-info").hide();
                            jQuery("#update-progress-group").show();
                            var update_progress_group = jQuery("#update-progress-group");
                            update_progress_group.show();
                            var update_progressbar = jQuery("#update-progressbar");
                            update_progressbar.width(json_obj["finish_precent"]);
                            update_progressbar.text("已更新:" + json_obj["finish_precent"]);

                            if (json_obj["bad_file_info"]["file_name"])
                            {
                                show_error_info.show();
                                var error_file_type = json_obj["bad_file_info"]["error_type"];
                                var filename = json_obj["bad_file_info"]["file_name"];
                                switch (error_file_type)
                                {
                                    case "BadZipfile":
                                        jQuery("#BadZipFile").show();
                                        jQuery("#show_BadZipFile_files").append("<li>"+ filename + "</li>");
                                        break;
                                    case "TypeError":
                                        jQuery("#TypeError").show();
                                        jQuery("#show_TypeError_files").append("<li>"+ filename + "</li>");
                                        break;
                                    case "IOError":
                                        jQuery("#IOError").show();
                                        jQuery("#show_IOError_files").append("<li>"+ filename + "</li>");
                                        break;
                                    default:
                                        break;
                                }
                            }
                        }
                        if (type === "load_data_finish")
                        {
                            // jQuery("#update-progress-group").hide();
                            window.able_search = true;
                            socket.close();
                            // alert("数据更新完成");
                        }
                    }
                }
            }
            catch (e) {
                log(e);
            }
        }
    });
});