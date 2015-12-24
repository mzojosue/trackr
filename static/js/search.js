function SearchCtrl ($timeout, $q, $log) {
  var self = this;
  self.querySearch = querySearch;
  self.searchTextChange = searchTextChange;
  self.selectedItemChange = selectedItemChange;

  function querySearch (query) {
    $log.log(query);
  }

  function searchTextChange (text) {
    $log.log('Text changed to ' + text);
  }

  function selectedItemChange (text) {
    $log.log('Item changed to ' + text);
  }
}