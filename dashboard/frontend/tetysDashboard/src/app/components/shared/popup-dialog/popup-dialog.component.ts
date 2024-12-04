import { Component, Input, OnChanges, SimpleChanges, ChangeDetectorRef, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DialogService } from '../../../services/popup-dialog.service'
import { timeout } from 'rxjs';

@Component({
  selector: 'popup-dialog',
  standalone: true,
  imports: [
    CommonModule
  ],
  templateUrl: './popup-dialog.component.html',
})
export class PopupDialogComponent implements OnChanges {

  @Input() position?:{ top: string, left: string }; // Position can be overridden
  @Input() extraContentClass = ''
  @Input() closeOnOutsideClick = true; // Optionally close the dialog on outside click
  @Output() onDialogCloseEvent: EventEmitter<boolean> = new EventEmitter<boolean>();

  constructor(
    private dialogService: DialogService,
    private cdr: ChangeDetectorRef
  ) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (this.position) {
      this.cdr.detectChanges();  // Ensures change detection is triggered after view initialization
    }
  }
  
  onOverlayClick(event: MouseEvent) {
    if (this.closeOnOutsideClick) {
      this.dialogService.hidePopup()
      this.onDialogCloseEvent.emit(true)
    }
  }

  getStyles() {
    if(this.position) {
      return {
        top: this.position.top,
        left: Number(this.position.left) - 4,
      };
    }
    return {}
  }
}
