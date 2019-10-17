import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ContractMgtDialogComponent } from './contract-mgt-dialog.component';
import {MAT_DIALOG_DATA, MatDialogModule, MatDialogRef, MatFormFieldModule} from '@angular/material';
import {RouterTestingModule} from '@angular/router/testing';
import {HttpClient} from '@angular/common/http';
import {HttpClientTestingModule, HttpTestingController} from '@angular/common/http/testing';
import {ReactiveFormsModule} from '@angular/forms';

describe('ContractMgtDialogComponent', () => {
  let component: ContractMgtDialogComponent;
  let fixture: ComponentFixture<ContractMgtDialogComponent>;
  let httpClient: HttpClient;
  let httpTestingController: HttpTestingController;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      imports: [
        MatDialogModule,
        RouterTestingModule,
        HttpClientTestingModule,
        ReactiveFormsModule,
        MatFormFieldModule,
      ],
      declarations: [ ContractMgtDialogComponent ],
      providers: [
        { provide: MatDialogRef, useValue: {} },
        { provide: MAT_DIALOG_DATA, useValue: {} }
      ],
    })
    .compileComponents();

    // Inject the http service and test controller for each test
    httpClient = TestBed.get(HttpClient);
    httpTestingController = TestBed.get(HttpTestingController);
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ContractMgtDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
