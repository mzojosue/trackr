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


function update_mat_list(selfID, matListID) {

  var jobNum = document.getElementById(selfID).value;
  $(matListID).load("/dynamic/j/" + jobNum + "/materials");

}


function unlock_job_for_editing(jobNum) {
    document.getElementById('jobAddress').readOnly = false;
    document.getElementById('jobDesc').readOnly = false;
    document.getElementById('foremanName').readOnly = false;
    document.getElementById('foremanPhone').readOnly = false;
    document.getElementById('foremanEmail').readOnly = false;
    document.getElementById('poPre').readOnly = false;

    //document.getElementById('unlockBtn').onclick = "document.forms['jobInfo'].submit();";
    //document.getElementById('unlockBtn').href = '/j/' + jobNum + '/update';

    var updateInfo = document.createElement('button');
    updateInfo.setAttribute('class', 'btn btn-sm btn-success');
    updateInfo.setAttribute('type', 'submit');
    updateInfo.setAttribute('form', 'jobInfo');
    updateInfo.innerHTML = 'Update';
    document.getElementById('jobHeader').appendChild(updateInfo);
}

function unlock_bid_for_editing(bidNum) {
    document.getElementById('bidDesc').readOnly = false;

    //document.getElementById('unlockBtn').onclick = "document.forms['jobInfo'].submit();";
    //document.getElementById('unlockBtn').href = '/j/' + jobNum + '/update';

    var updateInfo = document.createElement('button');
    updateInfo.setAttribute('class', 'btn btn-sm btn-success');
    updateInfo.setAttribute('type', 'submit');
    updateInfo.setAttribute('form', 'bidInfo');
    updateInfo.innerHTML = 'Update';
    document.getElementById('bidHeader').appendChild(updateInfo);
}

function add_quote_doc(job_num, m_hash, q_hash) {
    // set form action
    var url = '/j/' + job_num + '/material/' + m_hash + '/quote/' + q_hash + '/update/doc';
    var inputElement = document.getElementById('fileUpload-' + q_hash);
    inputElement.setAttribute('form', 'quoteUpdate');
    var fileForm = document.getElementById('quoteUpdate');
    fileForm.setAttribute('action', url);
    // submit form
    fileForm.submit();
    // refresh page
    //location.reload();
}

function unlock_table_for_editing() {
  // TODO:iterate over array to change object types
  var dataTypes = [['price-input', 'text'],
                   ['date-input', 'date']];
  //for (var i=0; i < dataTypes.length; i++) {
  //  var showCells = document.getElementsByClassName(dataTypes[i[0]]);
  //  for (var s=0; s < showCells.length; s++) {
  //    showCells[s].setAttribute('type', dataTypes[i[1]]);
  //  }
  //}

  var priceCells = document.getElementsByClassName('price-input');
  for (var i=0; i < priceCells.length; i++) {
    priceCells[i].setAttribute('type', 'text');
  }
  var dateCells = document.getElementsByClassName('date-input');
  for (var i=0; i < dateCells.length; i++) {
    dateCells[i].setAttribute('type', 'date');
  }
  var priceInputs = document.getElementsByClassName('hide-value');
  for (var i=0; i < priceInputs.length; i++) {
    priceInputs[i].style.display = 'none';
  }
}

//function update_po_attr(job_number, po_num, attr)

function unlock_sub_bids_for_editing() {
  var elements = [['due-date-label', 'date-input'],
      ['contact-label', 'gc_contact-input'],
      ['gc-label', 'gc-input']];

  for (var i=0; i < elements.length; i++) {
    var labels = document.getElementsByClassName(elements[i][0]);
    for (var z=0; z < labels.length; z++) {
      labels[z].style.display = 'none';        // Hide all label elements
    }

    var inputs = document.getElementsByClassName(elements[i][1]);
    for (var z=0; z < inputs.length; z++) {
      inputs[z].style.display = 'block';        // Show all input elements
    }
  }
}