
function openPopup(text, postUrl, postData) {
	if (postUrl != '')
		$.post(postUrl, postData).done(response => {
		if (response.text!=="")
			if (response.redirect) 
				window.location.href = response.text;
			else {
				$("#popup_text").html(response.text);
				$("#popup").fadeIn(200);
			}
		}).fail(() => openPopup('Verbindung zum Server fehlgeschlagen!', '', ''));
	else {
		$("#popup_text").html(text);
		$("#popup").fadeIn(200);
	}
}

function closePopup()
{
	$("#popup").fadeOut(200);
}