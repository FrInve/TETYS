import { Component, OnInit, ViewChild, ElementRef, AfterViewInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute } from '@angular/router';
import { NavbarComponent } from '../../components/shared/navbar/navbar.component'
import { PopupDialogComponent } from '../../components/shared/popup-dialog/popup-dialog.component';
import { DialogService } from '../../services/popup-dialog.service'
import { DateRangeService } from '../../services/date-range.service'
import { TopicCardComponent } from '../../components/shared/topic-card/topic-card.component';
import { LineChartComponent } from '../../components/shared/line-chart/line-chart.component';
import { TimeSettingCardComponent } from '../../components/time-setting-card/time-setting-card.component';
import { colorPallete } from '../../utils/fakeDB'
import { HintTooltipComponent } from '../../components/shared/hint-tooltip/hint-tooltip.component'
import { ApiService } from '../../services/api.service'
import { TopicDataModel } from '../../utils/models';
import { LoadingComponent } from '../../components/shared/loading/loading.component'
import { Subject } from 'rxjs';
import { debounceTime } from 'rxjs/operators';

@Component({
  selector: 'topics-comparison',
  standalone: true,
  imports: [
    CommonModule,
    NavbarComponent,
    PopupDialogComponent,
    TopicCardComponent,
    LineChartComponent,
    TimeSettingCardComponent,
    HintTooltipComponent,
    LoadingComponent
  ],
  templateUrl: './topics-comparison.component.html',
})

export class TopicsComparisonComponent implements OnInit, AfterViewInit  {
  private inputSubject: Subject<{ value: string, index: number }> = new Subject();

  @ViewChild('inputElement') inputElement!: ElementRef;

  searchTerm: string = ''
  mainArea: string = ''
  projectId = ''

  dialogPosition!: { top: string, left: string }

  selectedTopicsId: Set<string> = new Set()
  allowedTopicsNum = 5
  focusedInputIndex = 0
  searchHistory: {
    searchedTerm: '',
    selectedTopics: TopicDataModel[]
  }[] = [{
    searchedTerm: '',
    selectedTopics: []
  }]
  allTopics: TopicDataModel[][] = []
  chartData: any[] = []
  isLoading = false;

  constructor(
    private route: ActivatedRoute,
    private dialogService: DialogService,
    private dateRangeService: DateRangeService,
    private cdr: ChangeDetectorRef,
    private apiService: ApiService
  ) {
    // Debounce logic
    this.inputSubject.pipe(
      debounceTime(1000) // Wait for 1000ms after the last keypress
    ).subscribe(({ value, index }) => {
      this.getSearchedTopics(value, index);  // Call the API after debounce
    });
  }

  get isPopupOpen(): boolean {
    return this.dialogService.isPopupOpen
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

  get canDialogClosed(): boolean {
    return (this.searchHistory[this.focusedInputIndex] ? 
    this.searchHistory[this.focusedInputIndex].selectedTopics.length !== 0
    : false)
  }
  
  get isDialogOpen(): boolean {
    return this.dialogService.isPopupOpen
  }

  getBorderColor(inputIndex: number, topicIndex: number): string {
    let allSelectedTopicsNum = 0

    for (let index = 0; index < inputIndex; index++) {
      allSelectedTopicsNum = allSelectedTopicsNum + this.searchHistory[index].selectedTopics.length;
      
    }
    return colorPallete[allSelectedTopicsNum + topicIndex]
  }

  isFocused = (inputIndex: number): boolean => {
    return (this.dialogService.isPopupOpen && this.focusedInputIndex === inputIndex)
  }

  elementWidth = (inputIndex: number): number => {
    const { selectedTopics } = this.searchHistory[inputIndex]
    if (selectedTopics.length === 0) {
      return 20
    }
    return (selectedTopics.length * (100/this.allowedTopicsNum));
  }

  ngOnInit(): void {
    this.extractMacroAreaFromRoute();
    this.route.queryParams.subscribe(params => {
      this.searchTerm = params['searchTerm'];
      this.projectId = params['area'];
      this.searchHistory[0].searchedTerm = params['searchTerm'] 
    });
    this.chartData = [] //TODO: Fake data for line charts

    this.getSearchedTopics(this.searchTerm, 0)
  }

  ngAfterViewInit(): void {
    const rect = document.getElementById('searchInput_0')?.getBoundingClientRect();
    if (rect) {
      const top = rect.top + window.scrollY + rect.height; // Distance from top of the page
      const left = rect.left + window.scrollX; // Distance from left of the page
      this.dialogPosition = {
        top: `${top + 8}px`, //8px gap
        left: `${left}px`
      }
      // Manually trigger change detection after updating dialogPosition
      this.cdr.detectChanges();

      this.showTopicList()
    }
  }

  get timeResolution(): number {
    return this.dateRangeService.getResolution()
  }

  get getData() {
    return this.allTopics[this.focusedInputIndex]
  }

  get getRemainingTopicsNum(): number {
    return 5 - this.selectedTopicsId.size
  }

  getSearchedTopics = (searchedTerm: string, index: number) => {
    this.isLoading = true
    this.apiService.getData("topic", {
      project_id: this.projectId,
      keywords: searchedTerm
    }).subscribe({
      next: (res) => {
        this.allTopics[index] = res
      },
      complete: () => {
        this.isLoading = false
      }
    })
  }

  showTopicList = () => {
    this.dialogService.showPopup();
    // Scroll to the top
    window.scrollTo({
      top: 0,
      behavior: 'smooth'  // Optional for smooth scrolling
    });
    document.body.style.overflow = 'hidden';
  }

  hideTopicList = () => {
    this.dialogService.hidePopup()
    document.body.style.overflow = 'auto';
  }
  
  extractMacroAreaFromRoute = () => {
    const routePath = this.route.snapshot.url[0].path; // This gets the first segment like 'health'
    this.mainArea = routePath;
  }

  handleSearchInput = (e: Event) => {
    const target = e.target as HTMLInputElement
    const value = target.value;
    const index = this.focusedInputIndex;

    // Emit the input value and index to the Subject
    this.inputSubject.next({ value, index });
  }

  handleInputFocus = (e: FocusEvent, inputIndex: number) => {
    this.focusedInputIndex = inputIndex
    this.showTopicList()
  }

  handleTopicSelect = (obj: any, searchInputIndex: number) => {
    if (this.selectedTopicsId.has(obj.id)) {
      this.selectedTopicsId.delete(obj.id)
      this.searchHistory[searchInputIndex].selectedTopics = this.searchHistory[searchInputIndex].selectedTopics.filter((item) => {
        return this.selectedTopicsId.has(item.id.toString())
      })
      //TODO: should be deleted based on ID
      this.chartData = this.chartData.filter((d) => {
        return d.id !== obj.id.toString()
      })
    }else {
      if (this.selectedTopicsId.size < this.allowedTopicsNum) {
        this.selectedTopicsId.add(obj.id)
        this.searchHistory[searchInputIndex].selectedTopics.push(obj)
        var relativeFreq: number[] = []
        this.apiService.getData(
          `/topic/${obj.id}`, 
          {
            project_id: this.projectId
          }
        ).subscribe({
          next: (topicData) => {
            relativeFreq = topicData['relative_frequencies']
          },
          complete: () => {
            this.chartData = [
              ...this.chartData,
              {
                id: obj.id,
                data: relativeFreq
              }
            ]
          }
        })

      }
    }

    //Remove elements without selected topic
    this.searchHistory = this.searchHistory.filter((sh) => {
      return sh.selectedTopics.length !== 0
    })
    this.focusedInputIndex = this.searchHistory.length - 1 //adjust index after deleting an input

    //When searches are empty then close the topic list dialog
    if (this.searchHistory.length === 0) {
      this.hideTopicList()
    }
  }

  addSearchInput = () => {
    console.log(this.searchHistory, this.focusedInputIndex)
    this.searchHistory.push({
      searchedTerm: '',
      selectedTopics: []
    })
    this.focusedInputIndex++
    this.showTopicList()
  }

  timeResolutionChange = (e: Event) => {
    const inputValue = (e.target as HTMLInputElement).value;
    this.dateRangeService.setResolution(parseInt(inputValue))
    this.chartData = this.chartData.map((data) => {
      return {
        id: data.id,
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
