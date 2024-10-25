import { Component, Output, EventEmitter, Input } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';

@Component({
  selector: 'app-custom-input',
  standalone: true,
  imports: [],
  templateUrl: './custom-input.component.html',
})
export class CustomInputComponent {

  value: string = ''
  
  @Input() disabled: boolean = false

  @Output() valueChange: EventEmitter<string> = new EventEmitter<string>();
  @Output() exploreClick: EventEmitter<Event> = new EventEmitter<Event>();
  
  constructor( 
    public router :Router,
    private route: ActivatedRoute
  ) {}

  onInputChange(event: Event): void {
    const inputValue = (event.target as HTMLInputElement).value;
    this.value = inputValue
    this.valueChange.emit(inputValue);
  }

}
