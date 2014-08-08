var day = d3.time.format("%w"),
    week = d3.time.format("%U"),
    year = d3.time.format("%Y"),
    format = d3.time.format("%Y-%m-%d"),
    cellSize = 17;

drawYear = function(root_div, workshops) {
    var width = $("#year").parent().width(), // 960,
        height = 136,
        buckets = 8;

    cellSize = Math.floor(width / 53);
    height = cellSize * 7.5;

    var currentYear = parseInt(year(new Date()));

    var colors = ["#f7fcb9", "#d9f0a3", "#addd8e", "#78c679", "#41ab5d", "#238443", "#006837", "#004529"];
    // ["#ccece6", "#99d8c9", "#66c2a4", "#41ae76", "#238b45", "#006d2c", "#00441b"];

    var colorScale = d3.scale.quantile()
            .domain([0, 8])
            .range(colors);

    root_div.selectAll("svg").remove();

    var svg = root_div.selectAll("svg")
                .data([currentYear])
            .enter()
                .append("svg")
                .attr("width", width)
                .attr("height", height)
            .append("g")
                .attr("transform", "translate(" + ((width - cellSize * 53) / 2) + "," + (height - cellSize * 7 - 1) + ")");

    var rect = svg.selectAll(".day")
            .data(function(d) {
                return d3.time.days(new Date(d, 0, 1), new Date(d + 1, 0, 1));
            })
        .enter().append("rect")
            .attr("class", "day")
            .attr("width", cellSize)
            .attr("height", cellSize)
            .attr("x", function(d) {
                return week(d) * cellSize;
            })
            .attr("y", function(d) {
                return day(d) * cellSize;
            })
            .attr("fill", "#eee")
            .datum(format);

    rect.append("title")
            .text(function(d) { 
                return d; 
            });

    svg.selectAll(".month")
            .data(function(d) {
                return d3.time.months(new Date(currentYear, 0, 1), new Date(currentYear + 1, 0, 1));
            })
        .enter().append("path")
            .attr("class", "month")
            .attr("d", monthPath);

    var data = d3.nest()
            .key(function(d) {
                return d.date;
            })
            .rollup(function(d) {
                return d.length;
            })
            .map(workshops);

    rect.filter(function(d) {
                return data[d];
            })
            .attr("fill", function(d) {
                return colorScale(data[d]);
            });
}

function monthPath(t0) {
    var t1 = new Date(t0.getFullYear(), t0.getMonth() + 1, 0),
        d0 = +day(t0), w0 = +week(t0),
        d1 = +day(t1), w1 = +week(t1);

    return "M" + (w0 + 1) * cellSize + "," + d0 * cellSize
        + "H" + w0 * cellSize + "V" + 7 * cellSize
        + "H" + w1 * cellSize + "V" + (d1 + 1) * cellSize
        + "H" + (w1 + 1) * cellSize + "V" + 0
        + "H" + (w0 + 1) * cellSize + "Z";
}

// Easy way to bind multiple functions to window.onresize
// TODO: give a way to remove a function after its bound, other than removing all of them
utilsWindowResize = function(fun){
  if (fun === undefined) return;
  var oldresize = window.onresize;
  var params = Array.prototype.slice.call(arguments, 1);

  window.onresize = function(e) {
    if (typeof oldresize == 'function') oldresize(e);
    //fun(e);
    fun.apply(this, params);
  }
}
