import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { NavbarComponent } from '../../components/shared/navbar/navbar.component'
import { WordCloudComponent } from '../../components/shared/word-cloud/word-cloud.component';
import { RadarChartComponent } from '../../components/shared/radar-chart/radar-chart.component';
import { LineChartComponent } from '../../components/shared/line-chart/line-chart.component';
import { HintTooltipComponent } from '../../components/shared/hint-tooltip/hint-tooltip.component';
import { DateRangeService } from '../../services/date-range.service'
import { TimeSettingCardComponent } from '../../components/time-setting-card/time-setting-card.component'
import { RangeSliderComponent } from '../../components/shared/range-slider/range-slider.component'

@Component({
  selector: 'topic-details',
  standalone: true,
  imports: [
    CommonModule,
    NavbarComponent,
    WordCloudComponent,
    RadarChartComponent,
    LineChartComponent,
    TimeSettingCardComponent,
    RangeSliderComponent,
    HintTooltipComponent
  ],
  templateUrl: './topic-details.component.html',
})
export class TopicDetailsComponent {

  radarChartData: any[] = [];
  mainArea: string = '';
  selectedTab: string = 'Tab1';
  chartData: any[] = []
  chartData2: any[] = []

  firstInterval = { start: new Date(2024, 9, 7, 0, 5, 0, 0), end: new Date(2024, 9, 29, 23, 55, 0, 0)}
  secondInterval = { start: new Date(2024, 10, 7, 0, 5, 0, 0), end: new Date(2024, 11, 11, 23, 55, 0, 0)}

  gridResolution: number = 7
  
  constructor(
    private route: ActivatedRoute,
    private dateRangeService: DateRangeService
  ) {}

  get timeResolution(): number {
    return this.dateRangeService.getResolution()
  }

  get bgColor(): string {
    switch (this.mainArea) {
      case 'health':
        return "red"

      case 'economy':
        return "yellow"

      case 'inclusion':
        return "pink"

      case 'peace':
        return "purple"

      case 'sustainability':
        return "green"

      default:
        alert( "something went wrong!" );
        return ''
    }
  }

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      //TODO: later it should be given from API
      this.mainArea = params['area'];
    });
    this.radarChartData = this.generateRadarChartData(); 
    this.chartData = [
      {
        name: 'Topic Name',
        data: this.generateDatas(100)
      }
    ]
    this.chartData2 = [
      {
        name: 'Topic Name',
        data: this.generateDatas(100)
      }
    ]
  }

  generateRadarChartData(): any[] {
    const data: any[] = [];
    const categories = ['Health', 'Economy', 'Sustainability', 'Inclusion', 'Peace'];
  
    categories.forEach((category) => {
      data.push({
        category: category,
        value: Math.round(Math.random() * 100)
      });
    });
  
    return data;
  }

  selectTab(tab: string) {
    this.selectedTab = tab;
  }

  handleFirstIntervalChange = (intervals: {start: Date, end: Date}) => {
    this.firstInterval = intervals
  }

  handleSecondIntervalChange = (intervals: {start: Date, end: Date}) => {
    this.secondInterval = intervals
  }

  get firstRangeStart(): number {
    return this.dateToRange(this.firstInterval.start)
  }
  get firstRangeEnd(): number {
    return this.dateToRange(this.firstInterval.end)
  }
  get secondRangeStart(): number {
    return this.dateToRange(this.secondInterval.start)
  }
  get secondRangeEnd(): number {
    return this.dateToRange(this.secondInterval.end)
  }
  get getTimeResolution(): number {
    return this.dateRangeService.getResolution()
  }

  dateToRange(date: Date): number {
    const startTime = new Date('2024-09-14').setHours(0, 5, 0, 0)
    const endTime = new Date('2024-12-22').setHours(23, 59, 0, 0)

    const inputDate = date.getTime()

    const timeDiff = endTime - startTime;
    const scaledValue =((inputDate - startTime) / timeDiff) * 100

    return Math.max(0, Math.min(100, scaledValue))
  }

  gridResolutionChange = (e: Event) => {
    const inputValue = parseInt((e.target as HTMLInputElement).value);
    this.gridResolution = inputValue
  }

  timeResolutionChange = (e: Event) => {
    const inputValue = (e.target as HTMLInputElement).value;
    this.dateRangeService.setResolution(parseInt(inputValue))
    this.chartData = this.chartData.map((data) => {
      return {
        name: data.name,
        data: this.generateDatas(100/parseInt(inputValue), parseInt(inputValue))
      }
    })
  }

  //To Generate Fake data for the line chart
  generateDatas(count: number, timeResultion: number = 1) {
    let data = [];
    for (var i = 0; i < count; ++i) {
      let value = 100;
      value = Math.round((Math.random() * 10 - 5) + value); // Adjust the value randomly

      let date = new Date('2024-09-14');
      date.setHours(23, 59, 0, 0); // Set time to 23:59:00
      date.setDate(date.getDate() + i*timeResultion); // Increment the date by one day by default

      data.push({
        date: date.getTime(), // Get the timestamp
        value: value
      });
    }
    return data;
  }


  
}
