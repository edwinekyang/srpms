import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ContractFormElementComponent } from './contract-form-element.component';

describe('ContractFormElementComponent', () => {
  let component: ContractFormElementComponent;
  let fixture: ComponentFixture<ContractFormElementComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ ContractFormElementComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ContractFormElementComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
