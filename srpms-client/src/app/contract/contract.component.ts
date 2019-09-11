import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';

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
  constructor(private _http: HttpClient) {
    this._http.get('./api/research_mgt');
  }

  ngOnInit() {
    /*
    this._http.getBeer().subscribe(data => {
      this.brews = data;
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
