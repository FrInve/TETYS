import { Component, OnInit, Input, OnChanges, SimpleChanges, OnDestroy, AfterViewInit } from '@angular/core';
import * as am5 from "@amcharts/amcharts5";
import * as am5wc from "@amcharts/amcharts5/wc";
import am5themes_Animated from "@amcharts/amcharts5/themes/Animated";

@Component({
  selector: 'word-cloud',
  standalone: true,
  templateUrl: './word-cloud.component.html',
})

export class WordCloudComponent implements AfterViewInit, OnChanges, OnDestroy {

  @Input() chartId: string = '';
  @Input() wordData: { word: string; frequency: number }[] = []; // JSON data input

  private root!: am5.Root;
  private chart!: am5wc.WordCloud;

  ngAfterViewInit(): void {
    // Delay the initialization to ensure the DOM element is available
    setTimeout(() => {
      this.initChart();
    }, 500);
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['wordData'] && !changes['wordData'].isFirstChange()) {
      this.updateChart();
    }
  }

  private initChart() {
    if (!this.chartId) {
      console.error('Chart ID is required.');
      return;
    }

    // Create root element
    this.root = am5.Root.new(this.chartId);

    // Set themes
    this.root.setThemes([am5themes_Animated.new(this.root)]);

    // Create Word Cloud series
    this.chart = this.root.container.children.push(
      am5wc.WordCloud.new(this.root, {
        maxCount: 100,
        minWordLength: 2,
        maxFontSize: am5.percent(35),
      })
    );

    // Set the initial data
    this.chart.data.setAll(this.transformData(this.wordData));
    
    this.chart.labels.template.set("tooltipText", "{category}: [bold]{value}[/]");

    // Configure labels
    this.chart.labels.template.setAll({
      paddingTop: 5,
      paddingBottom: 5,
      paddingLeft: 5,
      paddingRight: 5,
    });
    this.updateChart();
  }

  private updateChart() {
    if (this.chart && this.wordData.length) {
      this.chart.data.setAll(this.transformData(this.wordData)); // Update data dynamically
    }
  }

  private transformData(wordData: { word: string; frequency: number }[]): any[] {
    return wordData.map(item => ({
      category: item.word,  
      value: item.frequency
    }));
  }

  ngOnDestroy(): void {
    if (this.root) {
      this.root.dispose();
    }
  }
}
