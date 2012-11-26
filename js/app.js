// Setup tables
var $table = $(".app-table");

var table = $table.find(".table").tablesorter({
    widthFixed: true,
    widgets: ['zebra']
});

console.log($table.find(".table-pager"));

table.tablesorterPager({
    container: $table.find(".table-pager"),
    positionFixed: false,
    size: 10
});

/*table.tablesorterMultiPageFilter({
    filterSelector: $table.find(".table-filter input")
});*/
