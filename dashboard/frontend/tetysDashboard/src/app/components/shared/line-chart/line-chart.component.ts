import { Component, Input, OnChanges, SimpleChanges, OnDestroy, AfterViewInit, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import * as am5 from "@amcharts/amcharts5";
import * as am5xy from "@amcharts/amcharts5/xy";
import am5themes_Animated from "@amcharts/amcharts5/themes/Animated";
import { colorPallete } from '../../../utils/fakeDB'
import { LegendTagsComponent } from '../legend-tags/legend-tags.component'
import { DateRangeService } from '../../../services/date-range.service'

@Component({
  selector: 'line-chart',
  standalone: true,
  imports: [LegendTagsComponent, CommonModule],
  templateUrl: './line-chart.component.html',
})

export class LineChartComponent implements OnDestroy, AfterViewInit, OnChanges {
  
  @Input() chartId: string = '';
  @Input() chartData: { data: any[], name: string }[] = [];
  @Input() timeResolution: number = 1;
  @Input() hasTag: boolean = true;

  @Input() hasTwoInterval: boolean = false;
  @Input() firstInterval!: { start: Date, end: Date }
  @Output() changeFirstInterval: EventEmitter<{start: Date, end: Date}> 
  = new EventEmitter<{start: Date, end: Date}>();
  @Input() secondInterval!: { start: Date, end: Date }
  @Output() changeSecondInterval: EventEmitter<{start: Date, end: Date}> 
  = new EventEmitter<{start: Date, end: Date}>();
  intervalsColor = ["#9563FF", "#EB7100"]

  @Input() hasGridSelection: boolean = false;
  @Input() gridResolution!: number
  selectedRanges: any[] = [];

  private root!: am5.Root;
  public chart!: am5xy.XYChart;
  private series!: am5xy.LineSeries;
  private dateAxis!: am5xy.DateAxis<am5xy.AxisRendererX>;
  private valueAxis!: am5xy.ValueAxis<am5xy.AxisRendererY>;

  constructor(
    private dateRangeService: DateRangeService,
  ){}

  ngAfterViewInit(): void {
    this.initChart();

    this.dateRangeService.dateRangeChange$.subscribe((data) => {
      this.onDatePickerChange(data.start, data.end)
    })
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['chartData'] && !changes['chartData'].isFirstChange()) {
      console.log("HAAAAAAAAAAAAAAAAAAAAAAAAAAAAA", changes['chartData'].currentValue)
      this.updateChart();
    }

    if( this.hasTwoInterval && changes["firstInterval"] ) {
      const range1 = this.dateAxis?.axisRanges.values[0]
      const range2 = this.dateAxis?.axisRanges.values[1]
      
      const tempStart = new Date(changes["firstInterval"].currentValue.start).getTime()
      const tempEnd = new Date(changes["firstInterval"].currentValue.end).getTime()

      if(range1 && range2) {
        range1.set("value", new Date(tempStart).setHours(0, 5, 0, 0));
        range1.set("endValue", new Date(tempEnd).setHours(23, 55, 0, 0));
        range2.set("value", new Date(tempEnd).setHours(23, 55, 0, 0));
      }
    }

    if( this.hasTwoInterval && changes["secondInterval"] ) {
      const range1 = this.dateAxis?.axisRanges.values[2]
      const range2 = this.dateAxis?.axisRanges.values[3]

      const tempStart = new Date(changes["secondInterval"].currentValue.start).getTime()
      const tempEnd = new Date(changes["secondInterval"].currentValue.end).getTime()

      if(range1 && range2) {
        range1.set("value", new Date(tempStart).setHours(0, 5, 0, 0));
        range1.set("endValue", new Date(tempEnd).setHours(23, 55, 0, 0));
        range2.set("value", new Date(tempEnd).setHours(23, 55, 0, 0));
      }
    }

    if( 
      this.gridResolution 
      && changes["gridResolution"] 
      && changes["gridResolution"].currentValue !== changes["gridResolution"].previousValue
    ) {
      if( this.dateAxis ) {
        // Get all the created axis ranges
        const allRanges = this.dateAxis.axisRanges;

        // Dispose of each axis range
        allRanges.each((range) => {
          range.dispose();
        });

        this.addGridColumns(new Date('2024-09-14'), new Date('2024-12-22'), this.gridResolution);  // 1 week intervals
      }
    }
  }

  get getChartSeries(): am5xy.LineSeries[] {
    return (this.chart?.series.values as am5xy.LineSeries[] || [])
  }

  private initChart() {
    this.root = am5.Root.new(this.chartId);

    // Set themes
    const myTheme = am5.Theme.new(this.root);
    // Move minor label a bit down
    myTheme.rule("AxisLabel", ["minor"]).setAll({
      dy: 1
    });
    // Tweak minor grid opacity
    myTheme.rule("Grid", ["minor"]).setAll({
      strokeOpacity: 0.08
    });
    this.root.setThemes([am5themes_Animated.new(this.root), myTheme]);

    // Create chart
    this.chart = this.root.container.children.push(am5xy.XYChart.new(this.root, {
      panX: false,
      panY: false,
      wheelX: "panX",
      wheelY: "zoomX",
      paddingLeft: 0,
    }));
  
    // Create DateAxis (X Axis)
    this.dateAxis = this.chart.xAxes.push(am5xy.DateAxis.new(this.root, {
      maxDeviation: 0,
      baseInterval: { timeUnit: "day", count: this.timeResolution }, //time resolution
      renderer: am5xy.AxisRendererX.new(this.root, {
        minorGridEnabled: true,
        minGridDistance: 200,    
        minorLabelsEnabled: true
      }),
      tooltip: am5.Tooltip.new(this.root, {})
    }));

    this.dateAxis.set("minorDateFormats", {
      day: "dd",
      month: "MM"
    });
    // Remove grid lines from X Axis
    this.dateAxis.get("renderer").grid.template.setAll({
      strokeOpacity: 0
    });

    //style the axis as needed
    this.dateAxis.setAll({
      y: -30, // Position it within the plotContainer
    });

    // Create ValueAxis (Y Axis)
    this.valueAxis = this.chart.yAxes.push(am5xy.ValueAxis.new(this.root, {
      renderer: am5xy.AxisRendererY.new(this.root, {})
    }));

    // Add cursor
    this.addCursorInteraction()

    this.updateChart();
  }

  onDatePickerChange(startDate: Date, endDate: Date) {
    const startPosition = this.dateAxis.dateToPosition(startDate);
    const endPosition = this.dateAxis.dateToPosition(endDate);
    const scrollbarX = this.chart.get("scrollbarX");
    if (scrollbarX) {
      scrollbarX.set("start", startPosition);
      scrollbarX.set("end", endPosition);
    }
  }

  private updateChart() {
    if (this.chartData && this.dateAxis) {
      // Clear existing series
      this.chart.series.clear();

      // Create a series for each data set
      this.chartData.forEach((dataSet, index) => {
        const series = this.chart.series.push(am5xy.LineSeries.new(this.root, {
          name: dataSet.name || `Series ${index + 1}`,
          xAxis: this.dateAxis,
          yAxis: this.valueAxis,
          valueYField: 'value',
          valueXField: 'date',
          legendValueText: "{valueY}",
          tooltip: am5.Tooltip.new(this.root, {
            labelText: "{valueY}"
          })
        }));

        // Add bullets (optional)
        series.bullets.push(() => {
          return am5.Bullet.new(this.root, {
            sprite: am5.Circle.new(this.root, {
              radius: 3.5,
              fill: series.get("fill"),
            })
          });
        });
        series.set("fill", am5.color(colorPallete[index]));
        series.set("stroke", am5.color(colorPallete[index]));
        series.strokes.template.setAll({
          strokeWidth: 2
        });
        // Set data for the series
        series.data.setAll(dataSet.data);
        this.dateAxis.data.setAll(this.chartData);
        // this.series = series
      });
      this.addScrollBar()
      // this.addLegend()
    }
  }

  private addScrollBar() {
    //Add scrollbar
    this.chart.set("scrollbarX", am5.Scrollbar.new(this.root, {
      orientation: "horizontal",
      height: 10
    }));

    let scrollbarX = this.chart.get("scrollbarX");
    if (scrollbarX) {
      scrollbarX.thumb.setAll({
        fill: am5.color("#8a8a8a"),
        stroke: am5.color("#8a8a8a"),
      });
      scrollbarX.startGrip.set("scale", 0.8);
      scrollbarX.endGrip.set("scale", 0.8);
      // Change the color of the grips (the buttons)
      scrollbarX.startGrip.get("background")!.setAll({
        fill: am5.color("#6e6e6e"),  // Set the fill color of the left grip (start grip)
        stroke: am5.color("#6e6e6e") // Set the stroke color of the left grip (start grip)
      });

      scrollbarX.endGrip.get("background")!.setAll({
        fill: am5.color("#6e6e6e"),  // Set the fill color of the right grip (end grip)
        stroke: am5.color("#6e6e6e") // Set the stroke color of the right grip (end grip)
      });

      
      var startLabel = scrollbarX.startGrip.children.push(am5.Label.new(this.root, {
        isMeasured: false,
        width: 100,
        fill: am5.color(0x000000),
        centerX: 45,
        centerY: 30,
        x: am5.p50,
        y: 0,
        fontWeight: '600',
        fontSize: '1rem',
        textAlign: "center",
        populateText: true
      }))

      scrollbarX.on("start", (position) => {
        setTimeout(() => {
          const startDate = this.dateAxis.positionToDate(position!);
          startLabel.set("text", this.root.dateFormatter.format(startDate, "MMM d, YYYY"));
          this.dateRangeService.setStartDate(this.formatDateToInputValue(startDate))
        }, 50);
      });

      var endLabel = scrollbarX.endGrip.children.push(am5.Label.new(this.root, {
        isMeasured: false,
        width: 100,
        fill: am5.color(0x000000),
        centerX: 70,
        centerY: 30,
        x: am5.p50,
        y: 0,
        fontWeight: '600',
        fontSize: '1rem',
        textAlign: "center",
        populateText: true
      }))

      scrollbarX.on("end", (position) => {
        setTimeout(() => {
          const endDate = this.dateAxis.positionToDate(position!);
          endDate.setDate(endDate.getDate() - 1);
          endLabel.set("text", this.root.dateFormatter.format(endDate, "MMM d, YYYY"))
          this.dateRangeService.setEndDate(this.formatDateToInputValue(endDate))
        }, 50);
      });

      this.chart.bottomAxesContainer.children.push(scrollbarX)
      this.chart.bottomAxesContainer.set("marginTop", 40); 
    }
  }

  private formatDateToInputValue(date: Date): string {
    try {
      const year = date.getFullYear();
      const month = (date.getMonth() + 1).toString().padStart(2, '0');  // Months are zero-based
      const day = date.getDate().toString().padStart(2, '0');

      return `${year}-${month}-${day}`;
    } catch (error) {
      return ''
    }
  }

  private addCursorInteraction() {
    var cursor = this.chart.set("cursor", am5xy.XYCursor.new(this.root, {}));
    // cursor.lineX.set("forceHidden", true);
    cursor.lineY.set("forceHidden", true);

    if(this.hasTwoInterval) {
      this.makeRange(
        this.firstInterval.start,
        this.firstInterval.end,
        this.intervalsColor[0], 
        0
      )

      this.makeRange(
        this.secondInterval.start,
        this.secondInterval.end,
        this.intervalsColor[1], 
        1
      )
    }

    if (this.hasGridSelection) {
      this.addGridColumns(new Date('2024-09-14'), new Date('2024-12-22'), this.gridResolution);  // 1 week intervals
    }

  }

  private addGridColumns(startDate: Date, endDate: Date, daysInterval: number) {
    let currentDate = startDate.getTime();
    const endDateTime = endDate.getTime();

    while (currentDate < endDateTime) {
      if(endDateTime - currentDate < 7 * 24 * 60 * 60 * 1000) break 
      const nextDate = new Date(currentDate + daysInterval * 24 * 60 * 60 * 1000);

      let rangeItem = this.dateAxis.createAxisRange(this.dateAxis.makeDataItem({}));
      rangeItem.set("value", currentDate);
      rangeItem.set("endValue", nextDate.getTime());

      rangeItem.get("grid")?.setAll({
        strokeOpacity: 1,
        stroke: am5.color("#6794dc")
      });

      let axisFill = rangeItem.get("axisFill");
      axisFill?.setAll({
        fillOpacity: 0.15,
        fill: am5.color("#ffffff"),
        visible:true,
        interactive: true, // Enable interactions
        cursorOverStyle: "pointer" // Set cursor to pointer on hover
      });

      axisFill?.events.on("click", () => this.toggleSelection(axisFill!, new Date(currentDate), nextDate));

      // Change color on hover
      axisFill?.events.on("pointerover", () => {
        axisFill?.set("fill", am5.color("#FFCC00"));  // Hover color
      });

      // Reset color when mouse leaves
      axisFill?.events.on("pointerout", () => {
        const isSelected = this.selectedRanges.some(
          (range) => range.start.getTime() === currentDate && range.end.getTime() === nextDate.getTime()
        );
        axisFill?.set("fill", am5.color(isSelected ? "#EB7100" : "#ffffff")); // Selected color or default color
      });

      currentDate = nextDate.getTime();
    }
  }

  private toggleSelection(gridRect: am5.Graphics, start: Date, end: Date) {
    const isSelected = this.isRangeSelected(start.getTime(), end.getTime());

    if (!isSelected) {
      gridRect.set("fill", am5.color("#EB7100"));  // Selected color
      this.selectedRanges.push({ start, end });
    } else {
      gridRect.set("fill", am5.color("#ffffff"));
      this.selectedRanges = this.selectedRanges.filter(
        (range) => range.start !== start && range.end !== end
      );
    }
  }

  ngOnDestroy(): void {
    if (this.root) {
      this.root.dispose();
    }
  }

  makeRange = (startDate: Date, endDate: Date, colorCode: string, index: number) => {
    var rangeTime1 = new Date(startDate).getTime()
    var rangeTime2 = new Date(endDate).getTime()

    new Date(rangeTime1).setHours(0, 0, 0, 0)
    new Date(rangeTime2).setHours(23, 59, 0, 0)

    var color = am5.color(colorCode);

    // add axis range 1
    var range1 = this.dateAxis.createAxisRange(this.dateAxis.makeDataItem({}));

    range1.set("value", rangeTime1);
    range1.set("endValue", rangeTime2);


    range1.get("grid")?.setAll({
      strokeOpacity: 1,
      stroke: color
    });


    var axisFill = range1.get("axisFill");
    axisFill?.setAll({
      fillOpacity: 0.15,
      fill: color,
      visible: true,
      draggable: false
    });

    // restrict from being dragged vertically
    axisFill!.adapters.add("y", function () {
      return 0;
    });

    // Store initial positions when dragging starts
    let initialPosition: number;
    let initialEndPosition: number;

    // axisFill!.events.on("dragstart", () => {
    //   const x = resizeButton1.x();
    //   initialPosition = this.dateAxis.toAxisPosition((x / this.chart.plotContainer.width()));
    //   initialEndPosition = this.dateAxis.toAxisPosition((x + axisFill!.width()) / this.chart.plotContainer.width());
    // });

    // axisFill!.events.on("dragstop", () => {

    //   var dx = axisFill!.x();
    //   var x = resizeButton1.x() + dx;

    //   var position = this.dateAxis.toAxisPosition((x / this.chart.plotContainer.width()));
    //   var endPosition = this.dateAxis.toAxisPosition((x + axisFill!.width()) / this.chart.plotContainer.width());

    //   // restrict from being dragged outside of plot
    //   if(position >= 0 && endPosition <= 1) {
    //     var value = this.dateAxis.positionToValue(position);
    //     var endValue = this.dateAxis.positionToValue(endPosition);

    //     if(index === 0) {
    //       this.changeFirstInterval.emit({
    //         start: new Date(new Date(value).setHours(0, 5, 0, 0)),
    //         end: new Date(new Date(endValue).setHours(23, 55, 0, 0))
    //       })
    //     }else {
    //       this.changeSecondInterval.emit({
    //         start: new Date(new Date(value).setHours(0, 5, 0, 0)),
    //         end: new Date(new Date(endValue).setHours(0, 5, 0, 0))
    //       })
    //     }

    //     range1.set("value", value);
    //     range1.set("endValue", endValue);
    //     range2.set("value", endValue);
  
    //     axisFill!.set("x", 0);
    //   }else {
    //     // If out of bounds, reset to initial positions
    //     const initialX = this.chart.plotContainer.width() * initialPosition;
    //     axisFill!.set("x", initialX - resizeButton1.x()); // Reset position
    //   }
    // })

    var resizeButton1 = am5.Button.new(this.root, {
      visible: false,
    });

    // set bullet for the range
    range1.set("bullet", am5xy.AxisBullet.new(this.root, {
      location:0,
      sprite: resizeButton1
    }));

    // add axis range 2
    var range2 = this.dateAxis.createAxisRange(this.dateAxis.makeDataItem({}));

    range2.set("value", rangeTime2);
    range2.get("grid")!.setAll({
      strokeOpacity: 1,
      stroke: color
    });

    var resizeButton2 = am5.Button.new(this.root, {
      visible: false,
    });

    // set bullet for the range
    range2.set("bullet", am5xy.AxisBullet.new(this.root, {
      sprite: resizeButton2
    }));
  }

  private isRangeSelected(startTime: number, endTime: number): boolean {
    return this.selectedRanges.some(range => 
      range.start.getTime() === startTime && range.end.getTime() === endTime
    );
  }
}
