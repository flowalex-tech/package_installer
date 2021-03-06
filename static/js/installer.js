var origin = window.location.origin;

$(function(){
  $('#selectAll').click(function() {
    if (this.checked) {
        $(':checkbox').each(function() {
            this.checked = true;
        });
    } else {
       $(':checkbox').each(function() {
            this.checked = false;
        });
    }
  });
  $("form").submit(function(){
    if(ga){
      console.log("ga present");
      var info = $(this).serialize().split("&");
      var version = info[0].split("=")[1];
      console.log(version);
      var packages = [];
      ga('send', 'event', 'install_version', version.replace("_", ""));
      info.slice(1).forEach(function(i){
        console.log(i);
        ga('send', 'event', 'install_package', i.split("=")[1]);
      });
    }
    var url = origin + "/get_installer?" + $(this).serialize();
    var command = "sudo apt-get install -y curl; curl '" + url + "' | sudo bash";
    $("#command-row pre").empty();
    $("#command-row pre").append(command);
    $("#command-row span").empty();
    $("#command-row span").append("<a href='"+url+"'>script link</a>");
    $("#command-row").show();
    return false;
  });

  $('[data-toggle="tooltip"]').tooltip()
})
