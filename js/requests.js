function displayWeeklyRequestsGraph(conversations) {
	displayRequestsGraph($('#container-weekly'), 'week', 'Requests per week', conversations)
}

function displayDailyRequestsGraph(conversations) {
    displayRequestsGraph($('#container-daily'), 'day', 'Requests per day', conversations)
}

function displayRequestsGraph(el, resolution, title, conversations) {
    conversations_deduplicated = removeDuplicateConversations(conversations);

    request_buckets = createBuckets(resolution, conversations_deduplicated);
    requests = bucketsToTimeseriesCounts(request_buckets);

    match_buckets = createBuckets(resolution, getMatchConversations(conversations));
    matches = bucketsToTimeseriesCounts(match_buckets);

    var options = getRequestGraphOptions(title, requests, matches);
    el.highcharts(options);
}

function getRequestGraphOptions(title, requests, matches) {
    return {
        chart: {
            zoomType: 'x'
        },
        title: {
            text: title
        },
        subtitle: {
            text: document.ontouchstart === undefined ?
                    'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
        },
        xAxis: {
            type: 'datetime'
        },
        yAxis: {
            title: {
                text: 'Number of requests'
            },
            min: 0
        },
        legend: {
            enabled: true
        },
        series: [
            {
                type: 'area',
                name: 'Number of requests',
                data: requests
            },
            {
                type: 'area',
                name: 'Number of matches',
                data: matches
            }
        ]
    }
}