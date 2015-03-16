function addMaterialItem() {
    var itemArea = document.getElementById('itemizedMaterialArea');
    var numi = document.getElementById('itemCounter');
    var num = (document.getElementById('itemCounter').value -1)+ 2;
    numi.value = num;

    // Create div to add number/qty input box to
    var qtyDiv = document.createElement('div');
    qtyDiv.setAttribute('class', 'col-xs-2');

    // Populate input element for quantity
    var qtyInput = document.createElement('input');
    var qtyIdName = 'item-'+num+'-qty';
    qtyInput.setAttribute('name', qtyIdName);
    qtyInput.setAttribute('type', 'number');
    qtyInput.setAttribute('class', 'form-control');
    qtyInput.setAttribute('value', '1');

    // Append qty input element to div
    qtyDiv.appendChild(qtyInput);


    // Create div to add item description input to
    var itemDiv = document.createElement('div');
    itemDiv.setAttribute('class', 'form-inline col-xs-10');

    // Populate input element for item description
    var itemInput = document.createElement('input');
    var itemIdName = 'item-'+num+'-desc';
    itemInput.setAttribute('name', itemIdName);
    itemInput.setAttribute('type', 'text');
    itemInput.setAttribute('class', 'form-control');
    itemInput.setAttribute('style', 'width: 90%;');
    itemInput.setAttribute('placeholder', 'Item Description Goes Here');

    // Create deletion button
    var itemDelete = document.createElement('a');
    var trashSpan  = document.createElement('span');
    itemDelete.setAttribute('class', 'btn btn-link');
    itemDelete.setAttribute('href', 'javascript:;');
    itemDelete.setAttribute('onclick', 'removeMaterialItem('+num+');');
    trashSpan.setAttribute('class', 'glyphicon glyphicon-trash');
    itemDelete.appendChild(trashSpan);

    // Append text input and delete button to div
    itemDiv.appendChild(itemInput);
    itemDiv.appendChild(itemDelete);

    var lineDiv = document.createElement('div');
    lineDiv.setAttribute('class', 'col-xs-12 form-group itemLineDiv');
    lineDiv.setAttribute('id', 'itemID-'+num);

    lineDiv.appendChild(qtyDiv);
    lineDiv.appendChild(itemDiv);

    itemArea.appendChild(lineDiv);
}




function removeMaterialItem(divNum) {

  var d = document.getElementById('itemizedMaterialArea');
  var getID = 'itemID-' + divNum;
  var olddiv = document.getElementById(getID);
  d.removeChild(olddiv);

}

// window.addEventListener('paste', ... or
document.onpaste = function(event){
  var items = (event.clipboardData || event.originalEvent.clipboardData).items;
  console.log(JSON.stringify(items)); // will give you the mime types
  var blob = items[0].getAsFile();
  var reader = new FileReader();
  reader.onload = function(event){
    console.log(event.target.result)}; // data url!
  reader.readAsDataURL(blob);
}

function update_mat_list() {

  var jobNum = document.getElementById("jobSelect").value;
  $("#materialList").load("/dynamic/j/" + jobNum + "/materials");

}