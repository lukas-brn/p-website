let tags = [];
const tagCounter = [];
let dragSrcElTag;

function addTag() { 
    const tag = $('#tag_input').val();
    $('#tag_input').val('')
    tags.push(tag);
    addTagManager(tags.length-1);
}

function removeTag(id) { 
    tags.splice(id, 1); 
    buildTagHtml();
}

function addTagManager(id) {
    $('#current_tag_div').append(`
        <div id="tag_outer_div_${ id }" class="tag_outer_div">
            <div id="tag_div_spacer_${ id }" class="tag_div_spacer">
                <p>Drop here</p>  
            </div>

            <div id="tag_div_${ id }" class="tag_div" draggable="true">
                <p id="tag_p_${ id }" class="tag_p">
                    ID: ${ id+1 }: ${ tags[id] }
                    <a onclick="removeTag(${ id })" style="cursor: pointer;">Delete</a>
                </p>
            </div>
        </div>
    `);
    $(`#tag_div_spacer_${ id }`).hide();
    tagCounter[id]=0;
    setupDragListenersTag(id);
}

function buildTagHtml() {
    let i = 0;
    $('#current_tag_div').html('');
    tags.forEach(() => addTagManager(i++));
}

function switchTags(id1, id2) {
    const el = tags[id1];

    tags[id1] = tags[id2];
    tags[id2] = el;
    buildTagHtml();
}

function pushTag(srcId, destId) {
    const src = tags[srcId]
    tags = tags.filter((src, i) => i!==srcId)
    if (destId > srcId) destId--;

    tags = tags.slice(0, destId).concat(src).concat(tags.slice(destId));
    buildTagHtml();
}

function handleDragStartTag(e) {
    this.style.opacity = '0.4';
    dragSrcElTag = this;
    e.dataTransfer.effectAllowed = 'move';
}

function handleDragOverTag(e) {
    if (e.preventDefault) e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    return false;
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

function handleDragEndTag(e) {
    this.classList.remove('over');
    this.style.opacity = 1;
}

function setupDragListenersTag(id) {
    const parent = $(`#tag_outer_div_${ id }`)[0];
    const spacer = parent.children[0];
    const file = parent.children[1];

    parent.addEventListener('dragenter', handleDragEnterTag, false);
    parent.addEventListener('dragover', handleDragOverTag, false);
    parent.addEventListener('dragleave', handleDragLeaveTag, false);
    file.addEventListener('dragend', handleDragEndTag, false);

    file.addEventListener('dragstart', handleDragStartTag, false);
    file.addEventListener('drop', handleDropTag, false);

    spacer.addEventListener('drop', handleSpacerDropTag, false);
}
