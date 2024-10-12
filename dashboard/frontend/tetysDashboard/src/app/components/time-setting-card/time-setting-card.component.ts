import { Component, Output, ViewChild, ElementRef, AfterViewInit, Input, NgZone, EventEmitter, OnInit } from '@angular/core';
import { DateRangeService } from '../../services/date-range.service'

@Component({
  selector: 'time-setting-card',
  standalone: true,
  imports: [],
  templateUrl: './time-setting-card.component.html',
})
export class TimeSettingCardComponent implements AfterViewInit{

  @ViewChild('startDatePicker', { static: true }) startDatePicker!: ElementRef<HTMLInputElement>;
  @ViewChild('endDatePicker', { static: true }) endDatePicker!: ElementRef<HTMLInputElement>;

  @Input() chartData: any[] = []
  @Output() chartDataChange = new EventEmitter<any[]>();

  minDate!: Date
  maxDate!: Date

  constructor(
    private dateRangeService: DateRangeService,
    private ngZone: NgZone
  ) {}

  ngAfterViewInit(): void {
    this.dateRangeService.setInputElement(this.startDatePicker, this.endDatePicker)  
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
    this.chartDataChange.emit(this.chartData)

  }

  dateRangeChanged = () => {
    var startDate = new Date(this.startDatePicker.nativeElement.value)
    var endDate = new Date(this.endDatePicker.nativeElement.value)
    if(startDate > endDate) {
      startDate = endDate
      endDate = new Date(this.startDatePicker.nativeElement.value)
    }
    startDate = startDate < this.minDate? this.minDate: startDate
    endDate = endDate > this.maxDate? this.maxDate: endDate

    this.startDatePicker.nativeElement.value = startDate.toISOString().split('T')[0]
    this.endDatePicker.nativeElement.value = endDate.toISOString().split('T')[0]

    this.dateRangeService.onDatePickerChange()
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
    let dates = data.map((item) => {
      return item.date
    })
    this.minDate = this.minDate < new Date(Math.min(...dates))? this.minDate: new Date(Math.min(...dates));
    this.maxDate = this.maxDate > new Date(Math.max(...dates))? this.maxDate: new Date(Math.max(...dates));

    return data;
  }
  
}
