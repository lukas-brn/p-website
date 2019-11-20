
let menuOpened = false;

function toggleMenu() {
	if(menuOpened){
		$("#main-nav").removeAttr("style");
	} else {
		$("#main-nav").css("height","100vh");
	}
	menuOpened = !menuOpened;
}
