import { Paper } from "../models/dbStructs";
import { GraphPageState, SearchPageState } from "../pages/GraphPageState";
import { GraphTicket } from "../pages/GraphTicket";

export interface AddPaperAction {
  type: "add_paper";
  payload: Paper;
}

export interface RemovePaperAction {
  type: "remove_paper";
  payload: Paper["code"];
}

export interface SetSourceAction {
  type: "set_source";
  payload: SearchPageState["source"];
}

export interface SetLimitAction {
  type: "set_limit";
  payload: SearchPageState["limit"];
}

export interface SetCursorAction {
  type: "set_cursor";
  payload: SearchPageState["cursor"];
}

export interface AddTicketAction {
  type: "add_ticket";
  payload: GraphTicket;
}

export interface RemoveTicketAction {
  type: "remove_ticket";
  payload: GraphPageState["selectedTicket"];
}

export interface RemoveExampleTicketsAction {
  type: "remove_example_tickets";
}

export interface SetYearRangeAction {
  type: "set_year_range";
  payload: GraphPageState["yearRange"];
}

export interface SetMonthAction {
  type: "set_month";
  payload: GraphPageState["month"];
}

export interface SetGroupingAction {
  type: "set_grouping";
  payload: GraphPageState["grouping"];
}

export interface SetSmoothingAction {
  type: "set_smoothing";
  payload: GraphPageState["smoothing"];
}

export interface SetSelectedTicketAction {
  type: "set_selected_ticket";
  payload: GraphPageState["selectedTicket"];
}
