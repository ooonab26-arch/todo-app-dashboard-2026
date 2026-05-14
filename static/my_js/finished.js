


function updatetag(noteId, newTag) {
    // /updatetag/{{ note.id }}?newtag=learn
    fetch(`/updatetag/${noteId}?newtag=${newTag}`)

    // get the span with the id tag_noteId
    let tagSpan = document.getElementById(`tag_${noteId}`)
    tagSpan.innerHTML = '#' + newTag  
}