/* eslint-disable no-undef, no-unused-vars */

let tags = [];
let dragSrcElTag;

function addTag() {
	tags.push($('#tag_input').val());
	$('#tag_input').val('');
	addTagManager(tags.length-1);
}

function removeTag(id) { 
	tags.splice(id, 1);
	buildTagHtml();
}

function addTagSpacer(id) {
	$('#current_tag_div').append(`<div id='tag_spacer_${ id }' class='tag_spacer' style='width: 100%; height: 10px;'></div>`);
	tagSpacerListeners(id);
}

function addTagManager(id) {
	$('#current_tag_div').append(`
		${ addElement('tag', id) }ID: ${ id+1 }: ${ tags[id] }</p>
		<a onclick="removeTag(${ id })" style="cursor: pointer;">Delete</a>
		<a onclick="tagPopup(${ id })" style="cursor: pointer;">Change Postiton</a>
	</div>
	`);
	addTagSpacer(id+1);
	setupDragListenersTag(id);
}

function buildTagHtml() {
	$('#current_tag_div').html('');
	addTagSpacer(0);
	tags.forEach((e, i) => addTagManager(i));
}

function pushTag(srcId, destId) {
	tags = pushElements(tags, srcId, destId);
	buildTagHtml();
}

// --- Drag and drop

function handleDragStartTag(e) {
	dragSrcElTag = this;
	handleDragStart(this, e);
}

function handleDragSpacerEnterTag(e) {
	const srcID = parseInt(dragSrcElTag.id.slice(8), 10);
	const thisID = parseInt(this.id.slice(11), 10);
	
	if (srcID !== thisID && srcID + 1 !== thisID) this.classList.add('over');
}

function handleDragSpacerLeaveTag(e) {
	this.classList.remove('over');
}

function handleSpacerDropTag(e) {
	if (e.stopPropagation) e.stopPropagation();
	this.parentElement.classList.remove('over');
	pushTag(parseInt(dragSrcElTag.id.slice(8), 10), parseInt(this.id.slice(11), 10));
	return false;
}

function setupDragListenersTag(id) {
	const dest = $(`#tag_div_${ id }`)[0];
	dest.addEventListener('dragend', handleDragEnd, false);
	dest.addEventListener('dragstart', handleDragStartTag, false);
}

function tagSpacerListeners(id) {
	const spacer = $(`#tag_spacer_${ id }`)[0];
	spacer.addEventListener('dragenter', handleDragSpacerEnterTag, false);
	spacer.addEventListener('dragover', handleDragOver, false);
	spacer.addEventListener('dragleave', handleDragSpacerLeaveTag, false);
	spacer.addEventListener('drop', handleSpacerDropTag, false);
}

buildTagHtml();