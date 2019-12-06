let data = new FormData();
let nextFileNum = 1;
let counter = [];
counter[0] = 0;
const captionInput = $("#caption_input").prop('value');
const bodyInput = $("#body_input").prop('value');

function set_file_input() {
    data.append(`file${ nextFileNum }`, $("#file_input").prop('files')[0]);
    add_to_manager(nextFileNum);
    $("#file_input").val("");
    nextFileNum++;
}

function add_to_manager(id) {
    $("#current_file_div").append(`
        <div id="file_outer_div_${ id }" class="file_outer_div">
            <div id="file_div_spacer_${ id }" class="file_div_spacer">
                <p>Drop here</p>  
            </div>

            <div id="file_div_${ id }" class="file_div" draggable="true">
                <p id="file_p_${ id }" class="file_p">
                    ID: ${ id }: Name: ${ data.get('file'+id).name }: Type: ${ data.get('file'+id).type }
                    <a onclick="delete_file(${ id })" style="cursor: pointer;">Delete</a>
                </p>
            </div>
        </div>
    `);
    $(`#file_div_spacer_${ id }`).hide();
    counter[id]=0;
    setup_drag_listeners(id);
}

function delete_file(id) {
    let data_tmp = new FormData();
    let i = 1;
    let count = 1;
    for (let pair of data.entries()) {
        if (i < id || i > id) {
            data_tmp.append('file' + count, pair[1]);
            count++;
        }
        i++;
    }
    data = data_tmp;
    build_html();
}

function switch_files(id1, id2) {
    let data_tmp = new FormData();
    let i = 1;
    let tmp_data_var;
    for (let pair of data.entries()) {
        if (i != id1 && i != id2) data_tmp.append(pair[0], pair[1]);
        else if (i == id1) {
            if (!tmp_data_var) {
                tmp_data_var = pair[1];
                data_tmp.append('file' + i, data.get('file' + id2));
            } else data_tmp.append('file' + i, tmp_data_var);
        } else if (i == id2) {
            if (!tmp_data_var) {
                tmp_data_var = pair[1];
                data_tmp.append('file' + i, data.get('file' + id1));
            } else data_tmp.append('file' + i, tmp_data_var);
        }
        i++;
    }
    data = data_tmp;
    build_html();
}

function push_file(srcId, destId) {
    let toPush = data.get(`file${ srcId }`);
    if (destId>srcId) destId--;
    delete_file(srcId);
    let data_tmp = new FormData();
    let write= 1;
    for ( let value of data.values() ) {
        if (write == destId) {
            data_tmp.append(`file${ write }`, toPush);
            data_tmp.append(`file${ ++write }`, value);
        } else data_tmp.append(`file${ write }`, value);
        write++;
    }
    data = data_tmp;
    build_html();
}

function build_html() {
    let i = 1;
    $("#current_file_div").html("");
    for (let key of data.keys()) {
        add_to_manager(i);
        i++;
    }
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
    const srcID = dragSrcEl.id.slice(9);
    const thisId = this.id.slice(15);

    this.classList.add('over');
    counter[thisId]++;
    if (srcID != thisId) $(`#file_div_spacer_${ thisId }`).show();
}

function handleDragLeave(e) {
    const thisId = this.id.slice(15)

    counter[thisId]--;
    if (counter[thisId] == 0) {
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
    if (dragSrcEl != this) switch_files(srcId, destId);
    return false;
}

function handleSpacerDrop(e) {
    const srcId = parseInt(dragSrcEl.id.slice(9));
    const destId = parseInt(this.id.slice(16));

    if (e.stopPropagation) e.stopPropagation();
    this.parentElement.classList.remove('over');
    counter[destId] = 0;
    push_file(srcId, destId);
    $(".file_div_spacer").hide();
    return false;
}

function handleDragEnd(e) {
    this.classList.remove('over');
    this.style.opacity = 1;
}

function setup_drag_listeners(id) {
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
