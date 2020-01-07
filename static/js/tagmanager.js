/* eslint-disable no-undef, no-unused-vars */

let tags = [];
const tagCounter = [];
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

function addTagManager(id) {
	$('#current_tag_div').append(`
		${ addElement('tag', id) }
		ID: ${ id+1 }: ${ tags[id] }
		<a onclick="removeTag(${ id })" style="cursor: pointer;">Delete</a>
		<a onclick="tagPopup(${ id })" style="cursor: pointer;">Change Postiton</a>
	</p></div></div>
	`);
	$(`#tag_div_spacer_${ id }`).hide();
	tagCounter[id]=0;
	setupDragListenersTag(id);
}

function buildTagHtml() {
	$('#current_tag_div').html('');
	tags.forEach((e, i) => addTagManager(i));
}

function switchTags(id1, id2) {
	tags = switchElements(tags, id1, id2);
	buildTagHtml();
}

function pushTag(srcId, destId) {
	tags = pushElements(tags, srcId, destId);
	buildTagHtml();
}

function handleDragStartTag(e) {
	dragSrcElTag = this;
	handleDragStart(this, e);
}

function handleDragEnterTag(e) {
	const srcID = parseInt(dragSrcElTag.id.slice(8));
	const thisId = parseInt(this.id.slice(14));

	this.classList.add('over');
	tagCounter[thisId]++;
	if (srcID !== thisId) $(`#tag_div_spacer_${ thisId }`).show();
}

function handleDragLeaveTag(e) {
	const thisId = parseInt(this.id.slice(14));

	tagCounter[thisId]--;
	if (tagCounter[thisId] === 0) {
		this.classList.remove('over');
		$(`#tag_div_spacer_${ thisId }`).hide();
	}
}

function handleDropTag(e) {
	const destId = parseInt(this.id.slice(8));
	const srcId = parseInt(dragSrcElTag.id.slice(8));

	if (e.stopPropagation) e.stopPropagation();
	this.parentElement.classList.remove('over');
	tagCounter[destId] = 0;
	if (dragSrcElTag !== this) switchTags(srcId, destId);
	return false;
}

function handleSpacerDropTag(e) {
	const srcId = parseInt(dragSrcElTag.id.slice(8));
	const destId = parseInt(this.id.slice(15));

	if (e.stopPropagation) e.stopPropagation();
	this.parentElement.classList.remove('over');
	tagCounter[destId] = 0;
	pushTag(srcId, destId);
	$('.tag_div_spacer').hide();
	return false;
}

function setupDragListenersTag(id) {
	const parent = $(`#tag_outer_div_${ id }`)[0];
	const spacer = parent.children[0];
	const file = parent.children[1];

	parent.addEventListener('dragenter', handleDragEnterTag, false);
	parent.addEventListener('dragover', handleDragOver, false);
	parent.addEventListener('dragleave', handleDragLeaveTag, false);
	file.addEventListener('dragend', handleDragEnd, false);

	file.addEventListener('dragstart', handleDragStartTag, false);
	file.addEventListener('drop', handleDropTag, false);

	spacer.addEventListener('drop', handleSpacerDropTag, false);
}
