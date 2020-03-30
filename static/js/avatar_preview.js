document.getElementById("avatar-file").onchange = function () {
    document.getElementById("avatar-label").innerHTML = this.files[0].name;

    var reader = new FileReader();
    reader.onload = function (e) {
        document.getElementById("avatar-img").src = e.target.result;
    };
    reader.readAsDataURL(this.files[0]);
};
