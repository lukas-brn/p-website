let data = new FormData();
let files;
let next_file_num = 1;

function set_file_input() {
    data.append(`file${ next_file_num }`, $("#file_input").prop('files')[0]);
    add_to_manager(next_file_num);
    $("#file_input").val("");
    next_file_num++;
}

function add_to_manager(id) {
    $("#current_file_div").append(`
            <div id="file_div_${ id }" class="file_div" draggable="true">
                <p id="file_p_${ id }" class="file_p">
                    ID: ${ id }: Name: ${ data.get('file'+id).name }: Type: ${ data.get('file'+id).type }
                    <a onclick="delete_file(${ id })" style="cursor: pointer;">Delete</a>
                </p>
            </div>
        `);
    setup_drag_listeners();
}

function delete_file(id) {
    data_tmp = new FormData();
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
    data_tmp = new FormData();
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
    this.classList.add('over');
}

function handleDragLeave(e) {
    this.classList.remove('over');
}

function handleDrop(e) {
    if (e.stopPropagation) e.stopPropagation();
    if (dragSrcEl != this) {
        let src_id = parseInt(dragSrcEl.id.slice(9));
        let dest_id = parseInt(this.id.slice(9));
        switch_files(src_id, dest_id);
    }
    return false;
}

function handleDragEnd(e) {
    [].forEach.call(files, function (file) {
        file.classList.remove('over');
        file.style.opacity = 1;
    });
}

function setup_drag_listeners() {
    files = document.querySelectorAll(".file_div");
    [].forEach.call(files, function (file) {
        file.addEventListener('dragstart', handleDragStart, false);
        file.addEventListener('dragenter', handleDragEnter, false);
        file.addEventListener('dragover', handleDragOver, false);
        file.addEventListener('dragleave', handleDragLeave, false);
        file.addEventListener('drop', handleDrop, false);
        file.addEventListener('dragend', handleDragEnd, false);
    });
}
