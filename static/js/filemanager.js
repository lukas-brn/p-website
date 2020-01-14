/* eslint-disable no-undef, no-unused-vars */

let files = [];
const fileCounter = [];
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

function addFileManager(id) {
	$('#current_file_div').append(`
		${ addElement('file', id) }
		ID: ${ id+1 }: Name: ${ files[id].name }: Type: ${ files[id].type }
		<a onclick="removeFile(${ id })" style="cursor: pointer;">Delete</a>
		<a onclick="filePopup(${ id })" style="cursor: pointer;">Change Postiton</a>
	</p></div></div>
	`);
	$(`#file_div_spacer_${ id }`).hide();
	fileCounter[id]=0;
	setupDragListenersFile(id);
}

function buildFileHtml() {
	$('#current_file_div').html('<b>Bilder</b>');
	files.forEach((e, i) => addFileManager(i));
}

function switchFiles(id1, id2) {
	files = switchElements(files, id1, id2);
	buildFileHtml();
}

function pushFile(srcId, destId) {
	files = pushElements(files, srcId, destId);
	buildFileHtml();
}

function handleDragStartFile(e) {
	dragSrcEl = this;
	handleDragStart(this, e);
}

function handleDragEnter(e) {
	const srcID = parseInt(dragSrcEl.id.slice(9), 10);
	const thisId = parseInt(this.id.slice(15), 10);
    
	this.classList.add('over');
	fileCounter[thisId]++;
	if (srcID !== thisId) $(`#file_div_spacer_${ thisId }`).show();
}

function handleDragLeave(e) {
	const thisId = this.id.slice(15);

	fileCounter[thisId]--;
	if (fileCounter[thisId] === 0) {
		this.classList.remove('over');
		$(`#file_div_spacer_${ thisId }`).hide();
	}
}

function handleDrop(e) {
	const destId = parseInt(this.id.slice(9), 10);
	const srcId = parseInt(dragSrcEl.id.slice(9), 10);

	if (e.stopPropagation) e.stopPropagation();
	this.parentElement.classList.remove('over');
	fileCounter[destId] = 0;
	if (dragSrcEl !== this) switchFiles(srcId, destId);
	return false;
}

function handleSpacerDrop(e) {
	const srcId = parseInt(dragSrcEl.id.slice(9), 10);
	const destId = parseInt(this.id.slice(16), 10);

	if (e.stopPropagation) e.stopPropagation();
	this.parentElement.classList.remove('over');
	fileCounter[destId] = 0;
	pushFile(srcId, destId);
	$('.file_div_spacer').hide();
	return false;
}

function setupDragListenersFile(id) {
	const parent = $(`#file_outer_div_${ id }`)[0];
	const spacer = parent.children[0];
	const file = parent.children[1];

	parent.addEventListener('dragenter', handleDragEnter, false);
	parent.addEventListener('dragover', handleDragOver, false);
	parent.addEventListener('dragleave', handleDragLeave, false);
	file.addEventListener('dragend', handleDragEnd, false);

	file.addEventListener('dragstart', handleDragStartFile, false);
	file.addEventListener('drop', handleDrop, false);

	spacer.addEventListener('drop', handleSpacerDrop, false);
}
