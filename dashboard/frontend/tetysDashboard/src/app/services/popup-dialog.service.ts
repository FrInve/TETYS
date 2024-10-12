import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})

export class DialogService {
    isPopupOpen = false;

    showPopup() {
      this.isPopupOpen = true;
    }
  
    hidePopup() {
      this.isPopupOpen = false;
    }
}
