import { Component, Input, OnChanges, SimpleChanges, OnDestroy, AfterViewInit, ElementRef } from '@angular/core';
import * as am5 from "@amcharts/amcharts5";
import * as am5radar from "@amcharts/amcharts5/radar";
import * as am5xy from "@amcharts/amcharts5/xy";
import am5themes_Animated from "@amcharts/amcharts5/themes/Animated";

@Component({
  selector: 'radar-chart',
  standalone: true,
  imports: [],
  templateUrl: './radar-chart.component.html',
})
export class RadarChartComponent implements OnDestroy, AfterViewInit, OnChanges {

  @Input() chartId: string = '';
  @Input() chartData: any[] = [];
  
  private root!: am5.Root;
  private chart!: am5radar.RadarChart;
  private series!: am5radar.RadarLineSeries;
  private xAxis!: am5xy.CategoryAxis<am5radar.AxisRendererCircular>;
  private yAxis!: am5xy.ValueAxis<am5radar.AxisRendererRadial>;

  constructor(private elementRef: ElementRef) { }

  ngAfterViewInit(): void {
    this.initChart();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['chartData'] && !changes['chartData'].isFirstChange()) {
      this.updateChart();
    }
  }

  private initChart() {
    this.root = am5.Root.new(this.chartId);

    this.root.setThemes([am5themes_Animated.new(this.root)]);

    this.chart = this.root.container.children.push(am5radar.RadarChart.new(this.root, {
      panX: false,
      panY: false,
      wheelX: "panX",
      wheelY: "zoomX",
    }));

    var cursor = this.chart.set("cursor", am5radar.RadarCursor.new(this.root, { }));
    
    cursor.lineY.set("visible", false);

    var xRenderer = am5radar.AxisRendererCircular.new(this.root, {});
    xRenderer.labels.template.setAll({
      radius: 10
    });

    this.xAxis = this.chart.xAxes.push(am5xy.CategoryAxis.new(this.root, {
      maxDeviation: 0,
      renderer: xRenderer,
      categoryField: "category",
    }));

    this.yAxis = this.chart.yAxes.push(am5xy.ValueAxis.new(this.root, {
      renderer: am5radar.AxisRendererRadial.new(this.root, {})
    }));

    this.series = this.chart.series.push(am5radar.RadarLineSeries.new(this.root, {
      name: "Series",
      xAxis: this.xAxis,
      yAxis: this.yAxis,
      valueYField: "value",
      categoryXField: "category",
      tooltip:am5.Tooltip.new(this.root, {
        labelText:"{valueY}"
      })
    }));

    this.series.strokes.template.setAll({
      strokeWidth: 2
    });

    this.series.set("fill", am5.color('#00A3FF'));
    this.series.set("stroke", am5.color('#00A3FF'));

    this.series.bullets.push(() => {
      return am5.Bullet.new(this.root, {
        sprite: am5.Circle.new(this.root, {
          radius: 5,
          fill: this.series.get("fill"),
        })
      });
    });

    this.updateChart();
  }

  private updateChart() {
    if (this.chartData && this.xAxis && this.series) {
      this.xAxis.data.setAll(this.chartData);
      this.series.data.setAll(this.chartData);
    }
  }

  ngOnDestroy(): void {
    if (this.root) {
      this.root.dispose();
    }
  }
}
