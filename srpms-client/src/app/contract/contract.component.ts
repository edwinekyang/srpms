import { Component, OnInit } from '@angular/core';
// import { HttpService } from '../http.service';

@Component({
  selector: 'app-contract',
  templateUrl: './contract.component.html',
  styleUrls: ['./contract.component.scss']
})
export class ContractComponent implements OnInit {

  firstName = '';
  lastName = '';
  // brews: Object;

  // tslint:disable-next-line:variable-name
  // constructor(private _http: HttpService) { }

  ngOnInit() {
    /*
    this._http.getBeer().subscribe(message => {
      this.brews = message;
      console.log(this.brews);
    });
     */
  }

  setClasses() {
    const myClasses = {
      active: this.firstName === 'a',
      notactive: this.firstName !== 'a',
    };
    return myClasses;
  }
}
