import { Component, ViewChild, ElementRef, Renderer2, Input, AfterViewInit, OnChanges, SimpleChanges, OnInit, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DateRangeService } from '../../../services/date-range.service'
@Component({
  selector: 'range-slider',
  standalone: true,
  imports: [
    CommonModule
  ],
  templateUrl: './range-slider.component.html',
})

export class RangeSliderComponent implements AfterViewInit, OnChanges, OnInit {

  @Input() id: string = 'rangeSlider'
  @Input() color: string = "#00CCB3"
  @Input() minRange: number = 1
  @Input() maxRange: number = 20
  @Output() changeRangeNumbers: EventEmitter<{start: Date, end: Date}> 
  = new EventEmitter<{start: Date, end: Date}>();

  minRangeValueGap = 7;

  minPercentage!: number
  maxPercentage!: number

  isDragging = false;
  startX!: number;
  elementStartX!: number;

  @ViewChild('range', { static: true }) range!: ElementRef<HTMLInputElement>;
  @ViewChild('minval', { static: true }) minval!: ElementRef<HTMLInputElement>;
  @ViewChild('maxval', { static: true }) maxval!: ElementRef<HTMLInputElement>;
  @ViewChild('rangeInputStart', { static: true }) rangeInputStart!: ElementRef<HTMLInputElement>;
  @ViewChild('rangeInputEnd', { static: true }) rangeInputEnd!: ElementRef<HTMLInputElement>;
  @ViewChild('parent', { static: true }) parentElement!: ElementRef<HTMLDivElement>;

  constructor(
    private renderer: Renderer2,
    private dateRangeService: DateRangeService
  ){}

  ngOnInit(): void {
    this.addDynamicStyles(this.color);
  }
  
  addDynamicStyles(color: string) {
    const style = this.renderer.createElement('style');
    style.innerHTML = `
      #${this.id}::-webkit-slider-thumb {
        height: 18px;
        width: 18px;
        border: none;
        background-color: ${color};
        pointer-events: auto;
        -webkit-appearance: none;
        cursor: pointer;
        margin-bottom: 1px;
      }

      #${this.id}::-moz-range-thumb {
        height: 14px;
        width: 14px;
        border: none;
        background-color: ${color};
        pointer-events: auto;
        -moz-appearance: none;
        cursor: pointer;
        margin-top: 30%;
      }
    `;
    this.renderer.appendChild(document.head, style);
  }

  ngOnChanges(changes: SimpleChanges): void {
    if(
      (
        changes["minRange"]?.currentValue 
        && 
        changes["minRange"].currentValue !== changes["minRange"].previousValue
      ) || (
        changes["maxRange"]?.currentValue 
        && 
        changes["maxRange"].currentValue !== changes["maxRange"].previousValue
      )) {
        this.setMinValueOutput()
        this.setMaxValueOutput()
        this.minRangeFill()
        this.maxRangeFill()
        this.MinVlaueBubbleStyle()
        this.MaxVlaueBubbleStyle()
    }

  }

  ngAfterViewInit(): void {
    // Initialize the starting position of the draggable element
    this.elementStartX = this.range.nativeElement.offsetLeft;
  }

  minRangeFill = () => {
    this.range.nativeElement.style.left = 
    Number(this.minRange) + "%";
  };
   
  maxRangeFill = () => {
    this.range.nativeElement.style.right =
    (100 - Number(this.maxRange)) + "%";
  };

  MinVlaueBubbleStyle = () => {
    let minPercentage = this.minRange;
    this.minval.nativeElement.style.left = minPercentage + "%";
    this.minval.nativeElement.style.transform = `translate(-${minPercentage / 2}%, -120%)`;
  };

  MaxVlaueBubbleStyle = () => {
    this.maxPercentage = 100 - this.maxRange;
    this.maxval.nativeElement.style.right = this.maxPercentage - 0.5 + "%";
    this.maxval.nativeElement.style.transform = `translate(${this.maxPercentage / 2}%, -120%)`;
  };
  
  setMinValueOutput = () => {
    // this.minRange = parseInt(this.rangeInputStart.nativeElement.value);
    this.minval.nativeElement.innerHTML = 
    this.rangeToDate(this.minRange)
    .toLocaleDateString(undefined, {    
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };
  
  setMaxValueOutput = () => {
    // this.maxRange = parseInt(this.rangeInputEnd.nativeElement.value);
    this.maxval.nativeElement.innerHTML = 
    this.rangeToDate(this.maxRange)
    .toLocaleDateString(undefined, {    
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };
  
  handleInputChange = (e: Event) => {
    const target = e.target as HTMLInputElement

    this.minRange = parseInt(this.rangeInputStart.nativeElement.value);
    this.maxRange = parseInt(this.rangeInputEnd.nativeElement.value);

    this.setMinValueOutput();
    this.setMaxValueOutput();
 
    this.minRangeFill();
    this.maxRangeFill();
 
    this.MinVlaueBubbleStyle();
    this.MaxVlaueBubbleStyle();

    if (this.maxRange - this.minRange < this.minRangeValueGap) {
      if (target.className === "min") {
        this.minRange = (this.maxRange - this.minRangeValueGap)
        this.setMinValueOutput();
        this.minRangeFill();
        this.MinVlaueBubbleStyle();
        target.style.zIndex = "2"
      } else {
        this.maxRange = (this.minRange + this.minRangeValueGap)
        target.style.zIndex = "2"
        this.setMaxValueOutput();
        this.maxRangeFill();
        this.MaxVlaueBubbleStyle();
      }
    }
    this.rangeInputStart.nativeElement.value = this.minRange.toString()
    this.rangeInputEnd.nativeElement.value = this.maxRange.toString()

    this.changeRangeNumbers.emit({
      start: this.rangeToDate(this.minRange),
      end: this.rangeToDate(this.maxRange)
    })
  }
  
  //Handle range drag and drop
  startDragging(event: MouseEvent | TouchEvent): void {
    this.isDragging = true;
    this.startX = this.getEventX(event);

    // Add event listeners for drag movement and stopping the drag
    document.addEventListener('mousemove', this.onDragging.bind(this));
    document.addEventListener('mouseup', this.stopDragging.bind(this));
    document.addEventListener('touchmove', this.onDragging.bind(this));
    document.addEventListener('touchend', this.stopDragging.bind(this));
  }

  onDragging(event: MouseEvent | TouchEvent): void {
    if (!this.isDragging) return;

    const currentX = this.getEventX(event);
    const deltaX = currentX - this.startX;

    // Calculate the new position
    let newLeftPosition = this.elementStartX + deltaX;

    // Ensure the element doesn't go outside the left and right boundaries of the parent
    const parentWidth = this.parentElement.nativeElement.offsetWidth;

    let newRangeNum = Math.floor(100*newLeftPosition/parentWidth)
    let rangeLength = Number(this.rangeInputEnd.nativeElement.value) - Number(this.rangeInputStart.nativeElement.value) 

    if (newRangeNum < 0) {
      newRangeNum = 0; // Don't go outside the left boundary
    } else if (newRangeNum + rangeLength > 100) {
      newRangeNum = 100 - rangeLength; // Don't go outside the right boundary
    }

    this.minRange = newRangeNum;
    this.maxRange = (rangeLength + newRangeNum);
    
    this.changeRangeNumbers.emit({
      start: this.rangeToDate(this.minRange),
      end: this.rangeToDate(this.maxRange)
    })

    this.setMinValueOutput();
    this.setMaxValueOutput();

    this.minRangeFill();
    this.maxRangeFill();

    this.MinVlaueBubbleStyle();
    this.MaxVlaueBubbleStyle();
  }

  stopDragging(): void {
    if (!this.isDragging) return;

    this.isDragging = false;
    this.elementStartX = this.range.nativeElement.offsetLeft;
    
    // Remove event listeners when the drag stops
    document.removeEventListener('mousemove', this.onDragging.bind(this));
    document.removeEventListener('mouseup', this.stopDragging.bind(this));
    document.removeEventListener('touchmove', this.onDragging.bind(this));
    document.removeEventListener('touchend', this.stopDragging.bind(this));
  }

  getEventX(event: MouseEvent | TouchEvent): number {
    return event instanceof MouseEvent ? event.clientX : event.touches[0].clientX;
  }

  //convert number range from 0 to 100 to a date
  rangeToDate(value: number): Date {
    // Ensure value is clamped between 0 and 100
    value = Math.max(0, Math.min(100, value));
  
    // Get the time in milliseconds for both startDate and endDate
    const startTime = new Date('2024-09-14').setHours(0, 5, 0, 0);
    const endTime = new Date('2024-12-22').setHours(23, 55, 0, 0);
  
    // Calculate the time difference
    const timeDiff = endTime - startTime;
  
    // Scale the value between 0 to 100 to the date range
    const scaledTime = startTime + (value / 100) * timeDiff;
  
    // Return the corresponding date
    return new Date(scaledTime)
  }
  
}
