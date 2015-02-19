function addElement() {
    var ni = document.getElementById('itemizedMaterialForm');
    var numi = document.getElementById('itemCounter');
    var num = (document.getElementById('itemCounter').value -1)+ 2;
    numi.value = num;
    var newdiv = document.createElement('div');
    var divIdName = 'my'+num+'Div';
    newdiv.setAttribute('id',divIdName);
    newdiv.innerHTML = 'Element Number '+num+' has been added! <a href=\'javascript:;\' onclick=\'removeElement('+divIdName+')\'>Remove the div "'+divIdName+'"</a>';
    ni.appendChild(newdiv);
}

function addMaterialItem() {
    var itemForm = document.getElementById('itemizedMaterialArea');
    var numi = document.getElementById('itemCounter');
    var num = (document.getElementById('itemCounter').value -1)+ 2;
    numi.value = num;

    // Create div to add number/qty input box to
    var qtyDiv = document.createElement('div');
    qtyDiv.setAttribute('class', 'col-xs-2');

    // Populate input element for quantity
    var qtyInput = document.createElement('input');
    var qtyIdName = 'item'+num+'-qty';
    qtyInput.setAttribute('id', qtyIdName);
    qtyInput.setAttribute('type', 'number');
    qtyInput.setAttribute('class', 'form-control');
    qtyInput.setAttribute('placeholder', '1');

    // Append qty input element to div
    qtyDiv.appendChild(qtyInput);


    // Create div to add item input to
    var itemDiv = document.createElement('div');
    itemDiv.setAttribute('class', 'col-xs-10');

    // Populate input element for quantity
    var itemInput = document.createElement('input');
    var itemIdName = 'item'+num+'-desc';
    itemInput.setAttribute('id', itemIdName);
    itemInput.setAttribute('type', 'text');
    itemInput.setAttribute('class', 'form-control');
    itemInput.setAttribute('placeholder', 'Write Item Description Here');

    // Append text input to div
    itemDiv.appendChild(itemInput);

    var lineDiv = document.createElement('div');
    lineDiv.setAttribute('id', 'itemLineDiv');
    lineDiv.setAttribute('class', 'col-xs-12 form-group');

    lineDiv.appendChild(qtyDiv);
    lineDiv.appendChild(itemDiv);

    itemForm.appendChild(lineDiv);
}

function removeElement(divNum) {

  var d = document.getElementById('itemizedMaterialForm');
  var olddiv = document.getElementById(divNum);
  d.removeChild(olddiv);

}

