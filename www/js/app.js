$(document).ready(function() {
    var $table = $(".app-table");

    // No box ad when we have adhesion, so #main-content gets 12 columns
    if (window.innerWidth <= 1024){
        $('#main-content').removeClass('col-md-8').addClass('col-md-12');
    }

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
