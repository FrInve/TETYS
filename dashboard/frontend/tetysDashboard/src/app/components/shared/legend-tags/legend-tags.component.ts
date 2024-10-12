import { Component, Input, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import * as am5 from "@amcharts/amcharts5";
import * as am5xy from "@amcharts/amcharts5/xy";
import { colorPallete } from '../../../utils/fakeDB'

@Component({
  selector: 'legend-tags',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './legend-tags.component.html',
})
export class LegendTagsComponent implements OnChanges{

  @Input() chartSeries: am5xy.LineSeries[] = [];

  focusedSeriesNames: Set<string> = new Set()

  IsFocused(series: am5xy.LineSeries): boolean {
    const seriesName = series.get("name")
    return this.focusedSeriesNames.has(seriesName!)
  }

  getBorderColor(index: number): string {
    return colorPallete[index]
  }

  ngOnChanges(changes: SimpleChanges): void {
    if(changes['chartSeries'].currentValue) {
      this.focusedSeriesNames = new Set()
    }
  }

  highlightSeries(series: am5xy.LineSeries) {
    this.chartSeries.forEach((lineSeries) => {
      if (lineSeries !== series) {
        // Dim the lines
        lineSeries.strokes.template.setAll({
          strokeOpacity: 0.1,
          stroke: am5.color(0x000000),
        });

        // Dim the bullets (dots)
        this.updateBulletColors(lineSeries, am5.color(0x000000), 0.1)

      } else {
        lineSeries.strokes.template.setAll({
          strokeWidth: 3
        });
      }
    });
  }

  resetHighlight() {
    this.chartSeries.forEach((lineSeries) => {
      lineSeries.strokes.template.setAll({
        strokeOpacity: 1,
        strokeWidth: 2,
        stroke: lineSeries.get("fill")
      });
      this.updateBulletColors(lineSeries, lineSeries.get("fill"), 1);
    });
  }

  focusSeries(series: am5xy.LineSeries) {
    // Check current visibility status
    const isVisible = series.get("visible");
    // Trigger the appropriate animation
    if (isVisible) {
      series.hide();
    } else {
      series.show();
    }

    const seriName = series.get('name')
    if(this.focusedSeriesNames.has(seriName!)) {
      this.focusedSeriesNames.delete(series.get('name')!)
    }else {
      this.focusedSeriesNames.add(series.get('name')!)
    }
  }

  updateBulletColors(series: am5xy.LineSeries, color?: am5.Color, opacity?: number) {
    series.dataItems.forEach((dataItem) => {
      const bullets = dataItem.bullets;
      if (bullets) {
        bullets.forEach((bullet) => {
          const sprite = bullet.get("sprite") as am5.Circle;  // Explicitly cast to am5.Circle
          if (sprite) {
            sprite.setAll({
              opacity: opacity,
              fill: color,  // Setting the fill color
              stroke: color // Optionally, also set the stroke color
            });
          }
        });
      }
    });
  }

}
