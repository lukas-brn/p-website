
// Event Listeners

$(window).resize(function() {
	closeNavOnDesktop();
});

// Functions

function toggleMenu()
{
	if($("#nav").attr("style") == "height: 100%;")
	{
		$("#nav").removeAttr("style");
		$("body").css("overflow-y", "scroll");
	}
	else
	{
		$("#nav").css("height", "100%");
		$("body").css("overflow-y", "hidden");
	}
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