
// Event Listeners

$(window).resize(function() {
	closeNavOnDesktop();
});

if(header)
{
	$(window).scroll(function() {
		headerActions();
	});
}

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

function headerActions() {
	if($(window).scrollTop() == 0)
	{
		$("#nav").removeAttr("bg");
	}
	else
	{
		$("#nav").attr("bg", "bg");
	}
	
	$("#header").css("background-position", "center "+$(window).scrollTop()*-0.3+"px");
}

headerActions();







