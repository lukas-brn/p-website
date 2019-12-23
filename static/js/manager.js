function addElement(type, id) {
    return `<div id="${ type }_outer_div_${ id }" class="${ type }_outer_div">
                <div id="${ type }_div_spacer_${ id }" class="${ type }_div_spacer">
                    <p>Drop here</p>  
                </div>

                <div id="${ type }_div_${ id }" class="${ type }_div" draggable="true">
                    <p id="${ type }_p_${ id }" class="${ type }_p">`
}

function switchElements(input, id1, id2) {
    const el = input[id1];
    input[id1] = input[id2];
    input[id2] = el;
    return input;
}

function pushElements(input, id1, id2) {
    const el = input[id1];
    input = input.filter((src, i) => i!==id1)
    if (id2 > id1) id2--;
    return input.slice(0, id2).concat(el).concat(input.slice(id2));
}

function handleDragStart(el, e) {
    el.style.opacity = '0.4';
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', this.innerHTML);
}

function handleDragOver(e) {
    if (e.preventDefault) e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    return false;
}

function handleDragEnd(e) {
    this.classList.remove('over');
    this.style.opacity = 1;
}