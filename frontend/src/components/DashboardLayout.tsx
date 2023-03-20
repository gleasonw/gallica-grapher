export default function DashboardLayout(props: { children: React.ReactNode }) {
  return (
    <div className="ml-10 mr-10 mb-10">
      <div className="justify-center items-center flex flex-col mt-10 gap-5 md:gap-10 lg:gap-10 xl:gap-10">
        {props.children}
      </div>
    </div>
  );
}
