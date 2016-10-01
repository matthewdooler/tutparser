$(document).ready(function() {
  $.ajaxSetup({ cache: false });
});

var input_date_format = 'DD/MM/YYYY'

function removeDuplicateConversations(conversations) {
    return _.uniqBy(conversations, function (e) {
      return e.coords + e.date + e.title;
    });
}

function getMatchConversations(conversations) {
    return _.filter(conversations, function(conversation, key) {
      return conversation['match'] == true;
    })
}

function createBuckets(resolution, conversations) {
    // Group conversations into buckets
    var buckets = _.groupBy(
        conversations, result =>
            moment(result['date'], input_date_format).startOf(resolution).toISOString()
        );

    // Add any missing buckets (i.e., buckets without any conversations)
    // TODO: This should really be a parameter as it should be possible to choose the same start date for lots of series of data, even if some are more sparse
    //var start = moment(_.min(Object.keys(buckets), function (key) { return buckets[key]; })).startOf(resolution);
    var start = moment("11/07/2016", input_date_format).startOf(resolution)
    var end = moment()
    for (var d = start; d.isBefore(end); d.add(1, resolution)) {
        dFormatted = d.toISOString()
        if (!(dFormatted in buckets)) {
            buckets[dFormatted] = []
        }
    }
    return buckets
}

function bucketsToTimeseriesCounts(buckets) {
    counts = []
    for (var key in buckets) {
      if (buckets.hasOwnProperty(key)) {
        counts.push([key, buckets[key].length])
      }
    }
    return counts.sort(function(a, b) { 
        idx = 0
        return moment(a[idx]) > moment(b[idx]) ? 1 : -1;
    });
}

$(function () {
    $.getJSON('data/conversations-with-coords.json', function (conversations) {
        displayWeeklyRequestsGraph(conversations);
        displayDailyRequestsGraph(conversations);
        displayCurrentStudents(conversations);
    });
});