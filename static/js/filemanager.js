let data = new FormData();
let nextFileNum = 1;
const counter = [];
counter[0] = 0;
let dragSrcEl;

function setFileInput() {
    data.append(`file${ nextFileNum }`, $('#file_input').prop('files')[0]);
    addToManager(nextFileNum);
    $('#file_input').val('');
    nextFileNum++;
}

function addToManager(id) {
    $('#current_file_div').append(`
        <div id="file_outer_div_${ id }" class="file_outer_div">
            <div id="file_div_spacer_${ id }" class="file_div_spacer">
                <p>Drop here</p>  
            </div>

            <div id="file_div_${ id }" class="file_div" draggable="true">
                <p id="file_p_${ id }" class="file_p">
                    ID: ${ id }: Name: ${ data.get(`file${ id }`).name }: Type: ${ data.get(`file${ id }`).type }
                    <a onclick="deleteFile(${ id })" style="cursor: pointer;">Delete</a>
                </p>
            </div>
        </div>
    `);
    $(`#file_div_spacer_${ id }`).hide();
    counter[id]=0;
    setupDragListeners(id);
}

function deleteFile(id) {
    const dataTmp = new FormData();
    let i = 1;
    let count = 0;
    for( let value of data.values() ) {
        if (i < id || i > id) dataTmp.append(`file${ ++count }`, value);
        i++;
    }
    data = dataTmp;
    build_html();
}

function switchFiles(id1, id2) {
    const dataTmp = new FormData();
    let i = 1;
    let tmpDataVar;
    for( [key, value] of data.entries()) {
        if (i !== id1 && i !== id2) dataTmp.append(key, value);
        else if (i === id1) {
            if (!tmpDataVar) {
                tmpDataVar = value;
                dataTmp.append(`file${ i }`, data.get(`file${ id2 }`));
            } else dataTmp.append(`file${ i }`, tmpDataVar);
        } else if (i === id2) {
            if (!tmpDataVar) {
                tmpDataVar = value;
                dataTmp.append(`file${ i }`, data.get(`file${ id1 }`));
            } else dataTmp.append(`file${ i }`, tmpDataVar);
        }
        i++;
    }
    data = dataTmp;
    buildHtml();
}

function pushFile(srcId, destId) {
    const dataTmp = new FormData();
    const toPush = data.get(`file${ srcId }`);

    if (destId > srcId) destId--;
    deleteFile(srcId);
    let write = 1;
    for( let value of data.values() ) {
        if (write === destId) {
            dataTmp.append(`file${ write }`, toPush);
            dataTmp.append(`file${ ++write }`, value);
        } else dataTmp.append(`file${ write }`, value);
        write++;
    }
    data = dataTmp;
    buildHtml();
}

function buildHtml() {
    let i = 0;
    $('#current_file_div').html('');
    for( let key of data.keys() ) addToManager(++i);
}

function handleDragStart(e) {
    this.style.opacity = '0.4';
    dragSrcEl = this;
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
}

function handleDragOver(e) {
    if (e.preventDefault) e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    return false;
}

function handleDragEnter(e) {
    this.classList.add('over');
    counter[thisId]++;
    if (srcID !== thisId) $(`#file_div_spacer_${ thisId }`).show();
}

function handleDragLeave(e) {
    const thisId = this.id.slice(15);

    counter[thisId]--;
    if (counter[thisId] === 0) {
        this.classList.remove('over');
        $(`#file_div_spacer_${ thisId }`).hide();
    }
}

function handleDrop(e) {
    const destId = parseInt(this.id.slice(9));
    const srcId = parseInt(dragSrcEl.id.slice(9));

    if (e.stopPropagation) e.stopPropagation();
    this.parentElement.classList.remove('over');
    counter[destId] = 0;
    if (dragSrcEl !== this) switchFiles(srcId, destId);
    return false;
}

function handleSpacerDrop(e) {
    const srcId = parseInt(dragSrcEl.id.slice(9));
    const destId = parseInt(this.id.slice(16));

    if (e.stopPropagation) e.stopPropagation();
    this.parentElement.classList.remove('over');
    counter[destId] = 0;
    pushFile(srcId, destId);
    $('.file_div_spacer').hide();
    return false;
}

function handleDragEnd(e) {
    [].forEach.call(files, function (file) {
        file.classList.remove('over');
        file.style.opacity = 1;
    });
}

function setupDragListeners(id) {
    const parent = $(`#file_outer_div_${ id }`)[0];
    const spacer = parent.children[0];
    const file = parent.children[1];

    parent.addEventListener('dragenter', handleDragEnter, false);
    parent.addEventListener('dragover', handleDragOver, false);
    parent.addEventListener('dragleave', handleDragLeave, false);
    file.addEventListener('dragend', handleDragEnd, false);

    file.addEventListener('dragstart', handleDragStart, false);
    file.addEventListener('drop', handleDrop, false);

    spacer.addEventListener('drop', handleSpacerDrop, false);
}
