import { Injectable, ElementRef } from '@angular/core';
import { BehaviorSubject, Subject } from 'rxjs';

@Injectable({
  providedIn: 'root'
})

export class DateRangeService {

  private startDateElement!: ElementRef;
  private endDateElement!: ElementRef;
  timeResolution: string = '1M'

  dateRangeChangeSubject = new Subject<{start: Date, end: Date}>();
  dateRangeChange$ = this.dateRangeChangeSubject.asObservable();

  setResolution(newRes: string) {
    this.timeResolution = newRes
  }

  getResolution(): string {
    return this.timeResolution
  }

  setInputElement(startElement: ElementRef, endElement: ElementRef) {
    this.startDateElement = startElement;
    this.endDateElement = endElement;
  }
  
  getStartDate(): string {
    return this.startDateElement.nativeElement.value;
  }

  getEndDate(): string {
    return this.endDateElement.nativeElement.value;
  }

  setStartDate(value: string) {
    if(this.startDateElement) {
      this.startDateElement.nativeElement.value = value;
    }
  }

  setEndDate(value: string) {
    if(this.endDateElement) {
      this.endDateElement.nativeElement.value = value;
    }
  }

  onDatePickerChange() {
    const startDateValue = this.startDateElement.nativeElement.value;
    const endDateValue = this.endDateElement.nativeElement.value;
    if (startDateValue && endDateValue) {
      const startDate = new Date(startDateValue);
      const endDate = new Date(endDateValue);
      this.dateRangeChangeSubject.next({
        start: startDate, 
        end: endDate
      });
    }
  }

}
