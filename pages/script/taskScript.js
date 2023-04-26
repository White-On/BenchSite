import {LineChart} from './dynamicPlot.js';
import {Histogram} from './histogram.js';
import {GroupedBarChart} from './groupedBarChart.js';

// to get the Task Name that we want to plot we have 2 options:

// 1. get the task name from an element in the html page
// let TaskName = document.querySelector('[id^="Task"]').id;
// console.log("TaskName = " + TaskName);

// 2. get the task name from the url
// var path = window.location.pathname;
// var page = path.split("/").pop().split(".")[0];
// console.log( page );

//3. get the task name from the title of the page
let TaskName = document.getElementById('entry-title').innerHTML;

let element = document.getElementById(TaskName);



let width = element.getBoundingClientRect().width;
// let height = window.innerHeight * 0.5;
let height = 500;

let chart;
// check if the arguments are numbers or not to sort the data if needed 
if (isNaN(importedData[0].arguments)){
    let orderingFunction = (a, b) => d3.ascending(a.runTime, b.runTime);
    importedData.sort(orderingFunction);
}

let allLibraries = importedData.map(d => d.libraryName);
allLibraries = [...new Set(allLibraries)];

handleClickToPrintCode([])

chart = GroupedBarChart(importedData, {
    values: d => d.runTime,
    categories: d => d.arguments,
    inerClass: d => d.libraryName,

    width: width,
    height: height,

    xLabel: "Arguments →",
    yLabel: "Run Time (ms) ↑",

    

    activationFunction: handleClickToPrintCode,

    margin: { top: 40, right: 10, bottom: 100, left: 50 },
    
});

function handleClickToPrintCode(elementsToDisplay) {
    // console.log(elementsToDisplay);
    for(let library of allLibraries){
        if(elementsToDisplay.includes(library)){
            document.getElementById(library).style.display = "block";
        }else{
            document.getElementById(library).style.display = "none";
        }
    }
}

element.appendChild(chart);

// document.body.innerHTML += code["pgmpy"]

//we want to make the navActive class active on the library page 
let navActive = document.getElementById(TaskName + "-nav");
navActive.classList.add("active");

navActive.parentElement.parentElement.getElementsByTagName('a')[0].classList.add("active");
navActive.parentElement.classList.replace("collapsed", "expanded");