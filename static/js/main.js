// Event Listeners

$(window).resize(function() {
	closeNavOnDesktop();
});

// Functions

function toggleMenu()
{
	$("#nav").attr("open", !($("#nav").attr("open")));
}

function closeNavOnDesktop()
{
	if($(window).width() > 900)
	{
		if($("#nav").attr("style") == "height: 100%;")
		{
			$("#nav").removeAttr("style");
			$("body").css("overflow-y", "scroll");
		}
	}
}







