import { Component, ViewChild } from '@angular/core';
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
import { ApiService } from '../../services/api.service'
import { LoadingComponent } from '../../components/shared/loading/loading.component'

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
    HintTooltipComponent,
    LoadingComponent
  ],
  templateUrl: './topic-details.component.html',
})
export class TopicDetailsComponent {

  @ViewChild(LineChartComponent) lineChartComponent!: LineChartComponent;

  topicId: string | null = null;
  radarChartData: any[] = [];
  mainArea: string = '';
  searchedKeyWord?: string
  similarityScore?: string

  selectedTab: string = 'Tab1';
  chartData: any[] = []
  chartData2: any[] = []

  topicDetails: {
    absolute_frequencies?: number[],
    end_date?: string,
    frequency?: string
    id?: number
    rankings?: number[]
    relative_frequencies?: number[]
    start_date?: string
    terms?: any[]
    title?: string
    total_documents?: number
  } = {}

  wordCloudData: {
    word: string, 
    frequency: number
  }[] = []

  firstInterval = { start: new Date(1500, 1, 1), end: new Date(1500, 1, 1)} //old date just for not be undefined
  secondInterval = { start: new Date(1500, 1, 1), end: new Date(1500, 1, 1)} //old date just for not be undefined

  gridResolution: number = 3 //number of months
  isLoading = false;

  //Publication props
  docList: {
    title: string,
    authors: string,
    date: string,
    reference: string,
    url: string
  }[] = []
  currentDocListLength = 10

  pValue!: number;
  hStatistic!: number;
  testPerformed = false;
  intervalsInfo = {
    start1: '', end1: '', start2: '', end2: ''
  }

  constructor(
    private route: ActivatedRoute,
    private dateRangeService: DateRangeService,
    private apiService: ApiService
  ) {}

  get timeResolution(): string {
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
    document.body.style.overflow = 'auto'; //If overflow hidden remianed from comparison page

    this.route.queryParams.subscribe(params => {
      this.mainArea = params['area'];
      this.searchedKeyWord = params['searchedKeyWord'];
      this.similarityScore = params['similarityScore'];
    });
    this.topicId = this.route.snapshot.paramMap.get('topicId');

    this.getRadarChartData(); 
    this.getTopicDetails();
    this.getPublicationList()
  }

  getTopicDetails = () => {
    this.isLoading = true
    var mappedData: any[] = []

    this.apiService.getData(
      `/topic/${this.topicId}`, 
      {
        project_id: this.macroAreaNameMap(this.mainArea),
        resolution: this.timeResolution
      }
    ).subscribe({
      next: (topicData) => {
        console.log("topicData", topicData)
        this.topicDetails = topicData
        this.topicDetails.terms?.forEach((term) => {
          this.wordCloudData.push({
            word: term[0], 
            frequency: term[1]
          })
        })
        mappedData = this.mapValuesToTimeResolution(
          topicData['relative_frequencies'], 
          topicData['start_date'], 
          topicData['end_date']
        );

        const [yearS, monthS, dayS] = topicData['start_date'].split('-').map(Number); // Split and convert each part to a number
        const [yearE, monthE, dayE] = topicData['end_date'].split('-').map(Number); // Split and convert each part to a number
        const formattedStartDate = new Date(yearS, monthS - 1, dayS);
        const formattedEndDate = new Date(yearE, monthE - 1, dayE);

        let duration = formattedEndDate.getTime() - formattedStartDate.getTime()

        this.firstInterval = {
          start: new Date(formattedStartDate.getTime() + duration/10),
          end: new Date(formattedStartDate.getTime() + 2*duration/5)
        }
        this.secondInterval = {
          start: new Date(formattedEndDate.getTime() - 2*duration/5),
          end: new Date(formattedEndDate.getTime() - duration/10)
        }
      },
      complete: () => {
        this.chartData = [
          {
            id: this.topicId,
            data: mappedData
          }
        ]
        this.chartData2 = [
          {
            id: '0' + this.topicId, //To differentiate IDs 
            data: mappedData
          }
        ]
        this.isLoading = false
      }
    })
  }

  getRadarChartData = () => {
    let data: any[] = [];

    this.apiService.getData(
      `/topic/${this.topicId}/terms`, 
      {
        project_id: this.macroAreaNameMap(this.mainArea),
        topic_id: this.topicId
      }
    ).subscribe({
      next: (chartDate) => {
        chartDate.terms.forEach((item: any[]) => {
          data.push({
            category: item[0],
            value: Math.round(100*item[1])
          });
        })
      },
      complete: () => {
        this.radarChartData = data;
      },
    })
  }

  getPublicationList = () => {
    this.apiService.getData(
      `/topic/${this.topicId}/documents`, 
      {
        project_id: this.macroAreaNameMap(this.mainArea),
        topic_id: this.topicId,
        size: this.currentDocListLength
      }
    ).subscribe({
      next: (docs) => {
        this.docList = docs
      },
    })
  }

  loadMore = () => {
    this.currentDocListLength = this.currentDocListLength + 5
    this.getPublicationList()
  }

  get canRunTest(): boolean {
    if (this.selectedTab === 'Tab2') {
      return this.lineChartComponent.selectedRanges.length > 1
    }
    return true
  }

  runStatisticalTest() {
    if(this.selectedTab === 'Tab1') {
      // Adjust start date to the first day of the month at midnight
      const adjustedStart1 = new Date(this.firstInterval.start.getFullYear(), this.firstInterval.start.getMonth(), 1);
      const adjustedStart2 = new Date(this.secondInterval.start.getFullYear(), this.secondInterval.start.getMonth(), 1);

      // Adjust end date to the last day of the month at 23:59:59
      const adjustedEnd1 = new Date(this.firstInterval.end.getFullYear(), this.firstInterval.end.getMonth() + 1, 0, 23, 59, 59);
      const adjustedEnd2 = new Date(this.secondInterval.end.getFullYear(), this.secondInterval.end.getMonth() + 1, 0, 23, 59, 59);

      let intevalValues1 = this.chartData[0].data.filter((point: { date: number, value: number}) => {
        const pointDate = new Date(point.date);
        return pointDate >= adjustedStart1 && pointDate <= adjustedEnd1;
      }).map((point: { date: number, value: number}) => point.value);

      let intevalValues2 = this.chartData[0].data.filter((point: { date: number, value: number}) => {
        const pointDate = new Date(point.date);
        return pointDate >= adjustedStart2 && pointDate <= adjustedEnd2;
      }).map((point: { date: number, value: number}) => point.value);

      this.apiService.postData(
        `/analysis/single_topic-two_intervals`, 
        {
          project_id: this.macroAreaNameMap(this.mainArea),
          topic_id: this.topicId,
          first_interval_values: intevalValues1,
          second_interval_values: intevalValues2
        }
      ).subscribe({
        next: (result) => {
          this.pValue = result['p_value']
          this.hStatistic = result['statistic']
        },
        complete:() => {
          this.intervalsInfo = {
            start1: this.formatDateToString(adjustedStart1),
            end1: this.formatDateToString(adjustedEnd1),
            start2: this.formatDateToString(adjustedStart2),
            end2: this.formatDateToString(adjustedEnd2)
          }
        },
      })
    }else {
      let intervalValues: number[] = []

      this.lineChartComponent.selectedRanges.forEach((sr) => {
        let tempValues = this.chartData2[0].data.filter((point: { date: number, value: number}) => {
          const pointDate = new Date(point.date);
          return pointDate >= sr.start && pointDate < sr.end;
        }).map((point: { date: number, value: number}) => point.value)

        intervalValues.push(tempValues)
      })

      this.apiService.postData(
        `/analysis/single_topic-multiple_intervals`, 
        {
          project_id: this.macroAreaNameMap(this.mainArea),
          topic_id: this.topicId,
          number_of_intervals: intervalValues.length,
          interval_values: intervalValues
        }
      ).subscribe({
        next: (result) => {
          console.log(result)
          this.pValue = result['p_value']
          this.hStatistic = result['statistic']
        },
      })
    }
    this.testPerformed = true;
  }

  formatDateToString(date: Date): string {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0'); // Months are 0-indexed
    const day = String(date.getDate()).padStart(2, '0');
  
    return `${year}-${month}-${day}`;
  }

  selectTab(tab: string) {
    this.selectedTab = tab;
    this.testPerformed = false
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

  dateToRange(date: Date): number {
    const startTime = new Date(this.topicDetails.start_date!).setHours(0, 5, 0, 0)
    const endTime = new Date(this.topicDetails.end_date!).setHours(23, 59, 0, 0)

    const inputDate = date.getTime()

    const timeDiff = endTime - startTime;
    const scaledValue =((inputDate - startTime) / timeDiff) * 100

    return Math.max(0, Math.min(100, scaledValue))
  }

  gridResolutionChange = (e: Event) => {
    const inputValue = parseInt((e.target as HTMLInputElement).value);
    this.gridResolution = inputValue

    // var mappedData: any[] = []
    // this.apiService.getData(
    //   `/topic/${this.topicId}`, 
    //   {
    //     project_id: this.macroAreaNameMap(this.mainArea),
    //     resolution: inputValue + 'M'
    //   }
    // ).subscribe({
    //   next: (topicData) => {
    //     mappedData = this.mapValuesToTimeResolution(
    //       topicData['relative_frequencies'], 
    //       topicData['start_date'], 
    //       topicData['end_date']
    //     );
    //   },
    //   complete: () => {
    //     this.chartData2 = [{
    //       id: this.topicId,
    //       data: mappedData
    //     }]
    //   }
    // })
  }

  timeResolutionChange = (e: Event) => {
    const inputValue = (e.target as HTMLInputElement).value;
    this.dateRangeService.setResolution(inputValue)

    var mappedData: any[] = []
    this.apiService.getData(
      `/topic/${this.topicId}`, 
      {
        project_id: this.macroAreaNameMap(this.mainArea),
        resolution: inputValue
      }
    ).subscribe({
      next: (topicData) => {
        mappedData = this.mapValuesToTimeResolution(
          topicData['relative_frequencies'], 
          topicData['start_date'], 
          topicData['end_date']
        );
      },
      complete: () => {
        this.chartData = [{
          id: this.topicId,
          data: mappedData
        }]
      }
    })
  }

  macroAreaNameMap = (area: string) => {
    switch (area) {
      case 'health':
        return 'human_needs'
      case 'economy':
        return 'economic_development'
      case 'inclusion':
        return'equality'
      case 'peace':
        return'global_partnership'
      case 'sustainability':
        return'environmental_sustainability'
      default:
        return;
    }
  }

  mapValuesToTimeResolution(
    values: number[], 
    startDate: Date, 
    endDate: Date
  ): { date: number, value: number }[] {
    const result: { date: number, value: number }[] = [];
    const totalMS = new Date(endDate).getTime() - new Date(startDate).getTime()
    const intervalMS = totalMS / (values.length - 1); 
    
    let currentDate = new Date(startDate).getTime();
  
    for (let i = 0; i < values.length; i++) {
      result.push({ date: currentDate, value: 100*values[i] });
  
      currentDate = currentDate + intervalMS; // Adjust date based on calculated interval
    }
    return result;
  }

  downloadCSV() {
    // Define headers
    const headers = ['Title', 'Authors', 'Date of Publication', 'Reference'];
    const rows = this.docList.map(doc => [
      `"${doc.title || '-'}"`,
      `"${doc.authors || '-'}"`,
      `"${doc.date || '-'}"`,
      `"${doc.reference || '-'}"`
    ]);

    const csvContent = [headers, ...rows]
      .map(e => e.join(','))
      .join('\n');

    // Create and download the file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'publications.csv';
    link.click();
    URL.revokeObjectURL(link.href); // Clean up
  }
  
}
