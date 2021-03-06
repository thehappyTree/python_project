$('.del_btn').click(function(evt) {
    evt.preventDefault();
    var carid = $(this).attr('id');
    $.confirm({
        title: '删除车辆信息！',
        content: '确认删除当前车辆信息？',
        type: 'red',
        autoClose: 'cancel|10000',
        buttons: {
            delCar: {
                text: '确认删除',
                btnClass: 'waves-effect waves-light btn red',
                action: function () {
                    $.ajax({
                        url: '/admin/cardel/',
                        type: "POST",
                        dataType: 'json',
                        data: {
                            'id': carid
                        },
                        success: function (data) {
                            if (data.is_success) {
                                Materialize.toast('车辆已删除！', 4000);
                            } else {
                                Materialize.toast('车辆信息错误！', 4000);
                            }
                            location.reload();
                        }
                    })
                }
            },
            cancel : {
                text : '取消',
                action : function(){
                }
            }

        }
    });
});

$('.modify_btn').click(function(evt) {
    evt.preventDefault();
    var carid = $(this).attr('id');
    $('#modify_modal').modal('open');
    $.ajax({
        url: '/admin/carmanage/',
        type: "POST",
        dataType: 'json',
        data: {
            'carid': carid
        },
        success: function (data) {
            if (data.is_success) {
                $('#e_serial').val(data.serial);
                $('#e_number_plate').val(data.number_plate);
            } else {
                Materialize.toast('车辆信息错误！', 4000);
                $('#modify_modal').modal('close');
            }
        }
    })
});

$("#number_plate").change(function() {
    var number_plate = $(this).val();
    $("#car_submit").addClass("disabled");
    $.ajax({
        url: '/admin/car_form_check/',
        type: "POST",
        dataType: 'json',
        data: {
            'number_plate': number_plate
        },
        success: function (data) {
             if (data.is_number_plate_taken) {
                 Materialize.toast('车牌号已存在！', 4000);
            }else{
                $("#car_submit").removeClass("disabled");
            }
        }
    });
});
/*
$("#number_plate").change(function() {
    var number_plate = $(this).val();
    $.ajax({
        url: '/admin/car_form_check/',
        type: "POST",
        dataType: 'json',
        data: {
            'number_plate': number_plate
        },
        uploadProgress: function() {
            $("#loading").show();
        },
        success: function (data) {
            if (data.is_number_plate_taken) {
                Materialize.toast('车牌号已存在！请检查输入！', 4000);
                $("#car_submit").addClass("disabled");
            } else if (!data.is_number_plate_taken) {
                $("#car_submit").removeClass("disabled");
            }
        }
    });
});
*/
var fileExtension = ['jpeg', 'jpg', 'png'];
$("#fimg").change(function() {
    var filename = $("#fimg").val();
    var extension = filename.replace(/^.*\./, '');
    if (extension == filename) {
        extension = '';
    } else {
        extension = extension.toLowerCase();
    }
    if ($.inArray(extension, fileExtension) == -1) {
        $("#car_submit").addClass("disabled");
        Materialize.toast('文件格式错误！请上传JPEG、JPG、PNG格式图片。', 4000);
    } else {
        $("#car_submit").removeClass("disabled");
    }
});

$("#bimg").change(function() {
    var filename = $("#fimg").val();
    var extension = filename.replace(/^.*\./, '');
    if (extension == filename) {
        extension = '';
    } else {
        extension = extension.toLowerCase();
    }
    if ($.inArray(extension, fileExtension) == -1) {
        $("#car_submit").addClass("disabled");
        Materialize.toast('文件格式错误！请上传JPEG、JPG、PNG格式图片。', 4000);
    } else {
        $("#car_submit").removeClass("disabled");
    }
});


$("#car_form").submit(function(){
    $("#loading").show();
    var serial = $("input[name='serial']").val();
    var number_plate = $("input[name='number_plate']").val();
    $(this).ajaxSubmit({
        url: '/admin/car_save/',
        type: "POST",
        dataType: 'json',
        data: {
            'serial': serial,
            'number_plate': number_plate
        },

        success: function (data) {
            location.reload();
            $("#loading").hide();
        }
    });
    return false;   //阻止表单默认提交
});


$("#car_modify").submit(function(){
    console.log("qwe123");
    /*
    $("#loading").show();
    var serial = $("input[name='e_serial']").val();
    var number_plate = $("input[name='e_number_plate']").val();
    $(this).ajaxSubmit({
        url: '/admin/car_save/',
        type: "POST",
        dataType: 'json',
        data: {
            'method': true,
            'serial': serial,
            'number_plate': number_plate
        },

        success: function (data) {
            location.reload();
            $("#loading").hide();
        }
    });
    return false;   //阻止表单默认提交
    */
});
