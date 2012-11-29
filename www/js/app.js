// Setup tables
var $table = $(".app-table");

$(function() {
    // JST example
    html = JST.example({ "name": "foobar" });

    console.log(html);

    // Tables example
    var table = $table.find(".table").tablesorter({
        widthFixed: true,
        widgets: ['zebra']
    });

    table.tablesorterPager({
        container: $table.find(".table-pager"),
        positionFixed: false,
        size: 10
    });

    table.tablesorterMultiPageFilter({
        filterSelector: $table.find(".table-filter input")
    });
});
