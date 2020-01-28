/* eslint-disable no-undef, no-unused-vars */

let files = [];
let dragSrcElFile;

function addFile() {
	files.push($('#file_input').prop('files')[0]);
	$('#file_input').val('');
	addFileManager(files.length - 1);
}

function removeFile(id) {
	files.splice(id,1);
	buildFileHtml();
}

function addFileSpacer(id) {
	$('#current_file_div').append(`<div id='file_spacer_${ id }' class='file_spacer' style='width: 100%; height: 10px;'></div>`);
	fileSpacerListeners(id);
}

function addFileManager(id) {
	$('#current_file_div').append(`
		${ addElement('file', id) }ID: ${ id+1 }: Name: ${ files[id].name }: Type: ${ files[id].type }</p>
		<a onclick="removeFile(${ id })" style="cursor: pointer;">Delete</a>
		<a onclick="filePopup(${ id })" style="cursor: pointer;">Change Postiton</a>
	</div>
	`);
	addFileSpacer(id+1);
	setupDragListenersFile(id);
}

function buildFileHtml() {
	$('#current_file_div').html('<b>Bilder</b>');
	addFileSpacer(0);
	files.forEach((e, i) => addFileManager(i));
}

function pushFile(srcId, destId) {
	files = pushElements(files, srcId, destId);
	buildFileHtml();
}

// --- Drag and drop

function handleDragStartFile(e) {
	dragSrcElFile = this;
	handleDragStart(this, e);
}

function handleDragSpacerEnterFile(e) {
	const srcID = parseInt(dragSrcElFile.id.slice(9), 10);
	const thisID = parseInt(this.id.slice(12), 10);
    
	if (srcID !== thisID && srcID + 1 !== thisID) this.classList.add('over');
}

function handleDragSpacerLeaveFile(e) {
	this.classList.remove('over');
}

function handleSpacerDropFile(e) {
	if (e.stopPropagation) e.stopPropagation();
	this.parentElement.classList.remove('over');
	pushFile(parseInt(dragSrcElFile.id.slice(9), 10), parseInt(this.id.slice(12), 10));
	return false;
}

function setupDragListenersFile(id) {
	const dest = $(`#file_div_${ id }`)[0];
	dest.addEventListener('dragend', handleDragEnd, false);
	dest.addEventListener('dragstart', handleDragStartFile, false);
}

function fileSpacerListeners(id) {
	const spacer = $(`#file_spacer_${ id }`)[0];
	spacer.addEventListener('dragenter', handleDragSpacerEnterFile, false);
	spacer.addEventListener('dragover', handleDragOver, false);
	spacer.addEventListener('dragleave', handleDragSpacerLeaveFile, false);
	spacer.addEventListener('drop', handleSpacerDropFile, false);
}

buildFileHtml();
